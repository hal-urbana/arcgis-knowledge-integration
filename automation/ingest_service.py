"""
Ingest Service
Orchestrates UDL ingestion into Esri Knowledge
"""

import logging
import time
import threading
import uuid
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from queue import Queue

from arcgis_knowledge_client import ArcGISKnowledgeClient
from udl_adapter import UDLAdapter, UDLConfig, UDLMessage
from transformer import Transformer, EsriKnowledgeEntity


logger = logging.getLogger(__name__)


@dataclass
class IngestConfig:
    """Configuration for the ingest service"""
    udl_config: UDLConfig
    arcgis_config: Dict[str, Any]
    topic: str
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    batch_size: int = 10
    max_backlog: int = 1000


class IngestionStats:
    """Track ingestion statistics"""
    def __init__(self):
        self.total_messages = 0
        self.success_count = 0
        self.fail_count = 0
        self.current_knowledge_graph_id: Optional[str] = None

    def update_success(self):
        self.total_messages += 1
        self.success_count += 1

    def update_failure(self):
        self.total_messages += 1
        self.fail_count += 1

    def get_success_rate(self) -> float:
        if self.total_messages == 0:
            return 0.0
        return (self.success_count / self.total_messages) * 100

    def get_summary(self) -> Dict[str, Any]:
        return {
            'total_messages': self.total_messages,
            'success_count': self.success_count,
            'fail_count': self.fail_count,
            'success_rate': round(self.get_success_rate(), 2),
            'current_kg_id': self.current_knowledge_graph_id
        }


class IngestService:
    """
    Service for ingesting UDL messages into Esri Knowledge
    """

    def __init__(
        self,
        ingest_config: IngestConfig,
        knowledge_graph_name: Optional[str] = None
    ):
        """
        Initialize ingest service

        Args:
            ingest_config: Ingest configuration
            knowledge_graph_name: Name for Esri Knowledge graph (auto-generated if None)
        """
        self.config = ingest_config
        self.stats = IngestionStats()
        self.uds_adapter = UDLAdapter(ingest_config.udl_config)
        self.transformer = Transformer(default_entity_type="Feature")
        self.arcgis_client = ArcGISKnowledgeClient(**ingest_config.arcgis_config)

        self._running = False
        self._thread = None
        self._batch_queue: Queue = Queue(maxsize=ingest_config.max_backlog)

        # Generate knowledge graph name if not provided
        if not knowledge_graph_name:
            knowledge_graph_name = f"UDL Ingest - {uuid.uuid4().hex[:6]}"

        self.knowledge_graph_name = knowledge_graph_name
        self.knowledge_graph: Optional[Any] = None

    def start(self):
        """Start the ingest service"""
        if self._running:
            logger.warning("Ingest service is already running")
            return

        logger.info(f"Starting ingest service for topic: {self.config.topic}")

        # Connect to ArcGIS Knowledge first
        self._connect_arcgis()

        # Create knowledge graph
        self._create_knowledge_graph()

        # Connect to UDL
        self.uds_adapter.connect()

        # Subscribe to topic
        self.uds_adapter.subscribe_to_topic(self.config.topic, auto_ack=False)

        self._running = True
        self._thread = threading.Thread(target=self._run_ingestion_loop, daemon=True)
        self._thread.start()

        logger.info("Ingest service started")

    def stop(self):
        """Stop the ingest service"""
        if not self._running:
            logger.warning("Ingest service is not running")
            return

        logger.info("Stopping ingest service...")

        self._running = False

        # Wait for thread to finish
        if self._thread:
            self._thread.join(timeout=10)

        # Close connections
        self.uds_adapter.disconnect()

        logger.info("Ingest service stopped")

    def _connect_arcgis(self):
        """Connect to ArcGIS Knowledge"""
        try:
            if not self.arcgis_client._auth_token:
                self.arcgis_client._authenticate()

            logger.info("Connected to ArcGIS Knowledge")
        except Exception as e:
            logger.error(f"Failed to connect to ArcGIS Knowledge: {e}")
            raise RuntimeError(f"ArcGIS Knowledge connection failed: {e}")

    def _create_knowledge_graph(self):
        """Create or get knowledge graph"""
        try:
            self.knowledge_graph = self.arcgis_client.create_knowledge_graph(
                title=self.knowledge_graph_name,
                description=f"Knowledge graph created from UDL topic: {self.config.topic}"
            )

            self.stats.current_knowledge_graph_id = self.knowledge_graph.id
            logger.info(f"Created knowledge graph: {self.knowledge_graph.id}")

        except Exception as e:
            logger.error(f"Failed to create knowledge graph: {e}")
            raise RuntimeError(f"Knowledge graph creation failed: {e}")

    def _run_ingestion_loop(self):
        """Main ingestion loop"""
        logger.info("Ingestion loop started")

        try:
            self.uds_adapter.consume_messages(
                topic=self.config.topic,
                callback=self._process_message,
                max_messages=None
            )

        except Exception as e:
            if self._running:  # Only log if we actually stopped
                logger.error(f"Error in ingestion loop: {e}")
                self._running = False

    def _process_message(self, udl_message: UDLMessage) -> bool:
        """
        Process a single UDL message

        Args:
            udl_message: Message from UDL

        Returns:
            bool: True if processed successfully
        """
        try:
            # Transform UDL message to Esri Knowledge entity
            entity = self.transformer.transform_message(udl_message)

            if not self.transformer.validate_entity(entity):
                logger.warning(f"Invalid entity: {entity}")
                self.stats.update_failure()
                return False

            # Add to batch queue
            self._batch_queue.put(entity)

            # Process batch if size reached or queue too full
            if self._batch_queue.qsize() >= self.config.batch_size:
                self._process_batch()

            # Check for backlog
            while self._batch_queue.qsize() >= self.config.max_backlog:
                time.sleep(0.1)
                logger.warning("Backlog building up, processing in background")

            self.stats.update_success()
            return True

        except Exception as e:
            logger.error(f"Error processing UDL message: {e}")
            self.stats.update_failure()
            return False

    def _process_batch(self):
        """Process a batch of entities"""
        batch = []
        while not self._batch_queue.empty():
            try:
                batch.append(self._batch_queue.get_nowait())
            except:
                break

        if not batch:
            return

        logger.info(f"Processing batch of {len(batch)} entities")

        # Batch submit to Esri Knowledge
        success_count = 0
        for entity in batch:
            try:
                # Add entity to knowledge graph
                self.arcgis_client.add_entity(
                    kg_id=self.knowledge_graph.id,
                    entity=entity
                )
                success_count += 1

            except Exception as e:
                logger.error(f"Failed to add entity {entity.id} to knowledge graph: {e}")

        logger.info(f"Batch processed: {success_count}/{len(batch)} successful")

    def get_status(self) -> Dict[str, Any]:
        """Get current ingest service status"""
        return {
            'running': self._running,
            'knowledge_graph_name': self.knowledge_graph_name,
            'knowledge_graph_id': self.knowledge_graph.id if self.knowledge_graph else None,
            'topic': self.config.topic,
            'batch_queue_size': self._batch_queue.qsize(),
            'statistics': self.stats.get_summary()
        }

    def reset_stats(self):
        """Reset ingestion statistics"""
        self.stats = IngestionStats()
        logger.info("Ingestion statistics reset")


# Convenience function for quick setup
def create_ingest_service_from_config(
    udl_host: str,
    udl_topic: str,
    arcgis_url: str,
    arcgis_username: str,
    arcgis_password: str,
    knowledge_graph_name: Optional[str] = None
) -> IngestService:
    """
    Create and start ingest service with common configuration

    Args:
        udl_host: UDL server host
        udl_topic: UDL topic to subscribe to
        arcgis_url: ArcGIS portal URL
        arcgis_username: ArcGIS username
        arcgis_password: ArcGIS password
        knowledge_graph_name: Name for knowledge graph

    Returns:
        IngestService: Configured and running ingest service
    """
    # Configure UDL connection
    udl_config = UDLConfig(
        host=udl_host,
        username=None,  # Will be provided separately
        password=None,  # Will be provided separately
        port=5672
    )

    # Configure Esri Knowledge connection
    arcgis_config = {
        'portal_url': arcgis_url,
        'username': arcgis_username,
        'password': arcgis_password
    }

    # Create ingest config
    ingest_config = IngestConfig(
        udl_config=udl_config,
        arcgis_config=arcgis_config,
        topic=udl_topic,
        batch_size=10,
        max_backlog=1000
    )

    # Create and start service
    service = IngestService(
        ingest_config=ingest_config,
        knowledge_graph_name=knowledge_graph_name
    )

    service.start()

    return service