"""
UdL Adapter
Handles connection, authentication, and topic subscription with Unified Data Library
"""

import json
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import time
import ssl
import pika


@dataclass
class UDLConfig:
    """Configuration for Unified Data Library connection"""
    host: str
    port: int = 5672
    username: str = None
    password: str = None
    virtual_host: str = "/"
    exchange: str = "udl.public"
    message_expiration: int = 300000  # 5 minutes in milliseconds
    ssl_verify: bool = True


@dataclass
class UDLMessage:
    """Represents a message from UDL"""
    body: Dict[str, Any]
    properties: Dict[str, Any]
    headers: Dict[str, Any]
    delivery_tag: Optional[str] = None


logger = logging.getLogger(__name__)


class UDLError(Exception):
    """Base class for UDL errors"""
    pass


class UDLSecurityError(UDLError):
    """Raised when authentication or security check fails"""
    pass


class UDLConnectionError(UDLError):
    """Raised when connection to UDL fails"""
    pass


class UDLAdapter:
    """
    Adapter for Unified Data Library message broker
    """

    def __init__(self, config: UDLConfig):
        """
        Initialize UDL adapter with configuration

        Args:
            config: UDL configuration object
        """
        self.config = config
        self.connection = None
        self.channel = None
        self._is_connected = False
        self.message_callback: Optional[Callable[[UDLMessage], Any]] = None

    def connect(self) -> bool:
        """
        Establish connection to UDL server

        Returns:
            bool: Connection success
        """
        try:
            # Build connection parameters
            credentials = pika.PlainCredentials(
                self.config.username,
                self.config.password
            )

            parameters = pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                virtual_host=self.config.virtual_host,
                credentials=credentials,
                ssl_options=self._get_ssl_options(),
                connection_attempts=3,
                retry_delay=5
            )

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Set QoS to prefetch one message at a time for backpressure control
            self.channel.basic_qos(prefetch_count=1)

            logger.info(f"Connected to UDL at {self.config.host}:{self.config.port}")
            self._is_connected = True
            return True

        except pika.exceptions.AMQPConnectionError as e:
            self._is_connected = False
            logger.error(f"Failed to connect to UDL: {e}")
            raise UDLConnectionError(f"Connection failed: {e}")
        except Exception as e:
            self._is_connected = False
            logger.error(f"Unexpected error during connection: {e}")
            raise UDLError(f"Connection error: {e}")

    def _get_ssl_options(self) -> Optional[pika.SSLOptions]:
        """
        Get SSL options if SSL is enabled

        Returns:
            SSLOptions or None
        """
        if not self.config.ssl_verify and self.config.host.startswith("https"):
            return pika.SSLOptions(ssl.create_default_context())
        return None

    def subscribe_to_topic(
        self,
        topic: str,
        auto_ack: bool = False
    ) -> bool:
        """
        Subscribe to a UDL topic

        Args:
            topic: Topic name to subscribe to
            auto_ack: If True, auto-acknowledge delivered messages

        Returns:
            bool: Subscription success
        """
        if not self._is_connected:
            raise UDLConnectionError("Not connected to UDL")

        try:
            # Declare queue and bind to exchange with topic pattern
            self.channel.queue_declare(
                queue=topic,
                durable=True,
                arguments={
                    'x-message-ttl': self.config.message_expiration,
                    'x-dead-letter-exchange': 'udl.dlq'
                }
            )

            self.channel.queue_bind(
                exchange=self.config.exchange,
                queue=topic,
                routing_key=topic
            )

            logger.info(f"Subscribed to topic: {topic}")
            return True

        except Exception as e:
            logger.error(f"Failed to subscribe to topic {topic}: {e}")
            raise UDLError(f"Subscription failed: {e}")

    def consume_messages(
        self,
        topic: str,
        callback: Callable[[UDLMessage], Any],
        max_messages: Optional[int] = None
    ) -> None:
        """
        Consume messages from a topic

        Args:
            topic: Topic name to consume from
            callback: Function to call on each message
            max_messages: Maximum number of messages to consume (None = infinite)
        """
        if not self._is_connected:
            raise UDLConnectionError("Not connected to UDL")

        self.message_callback = callback
        message_count = 0

        def on_message(ch, method, properties, body):
            """Internal callback for Pika"""
            try:
                message = self._parse_message(body, properties, method.delivery_tag)

                # Call the user-provided callback
                result = callback(message)

                # Acknowledge if auto_ack is False and callback succeeded
                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                message_count += 1
                if max_messages and message_count >= max_messages:
                    ch.stop_consuming()
                    logger.info(f"Consumed {max_messages} messages, stopping")

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                if not auto_ack:
                    # Negative acknowledgement to requeue
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        self.channel.basic_consume(
            queue=topic,
            on_message_callback=on_message,
            auto_ack=auto_ack
        )

        logger.info(f"Starting to consume from topic: {topic}")
        self.channel.start_consuming()

    def _parse_message(
        self,
        body: bytes,
        properties: pika.BasicProperties,
        delivery_tag: str
    ) -> UDLMessage:
        """
        Parse raw message into UDLMessage object

        Args:
            body: Raw message body
            properties: Pika properties
            delivery_tag: Delivery tag for acknowledgment

        Returns:
            UDLMessage: Parsed message
        """
        try:
            message_body = json.loads(body.decode('utf-8'))

            # Get properties and headers from Pika
            headers = {}
            if properties.headers:
                headers = {k: v for k, v in properties.headers.items()}

            # Extract standard properties
            properties_dict = {
                'content_type': properties.content_type,
                'content_encoding': properties.content_encoding,
                'message_id': properties.message_id,
                'timestamp': properties.timestamp.timestamp() if properties.timestamp else None,
                'expiration': properties.expiration,
                'priority': properties.priority,
                'reply_to': properties.reply_to,
                'correlation_id': properties.correlation_id
            }

            return UDLMessage(
                body=message_body,
                properties=properties_dict,
                headers=headers,
                delivery_tag=delivery_tag
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message body: {e}")
            raise UDLError(f"Invalid JSON in message body: {e}")

    def disconnect(self):
        """Close connection to UDL"""
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()

        if self.connection and self.connection.is_open:
            self.connection.close()

        self._is_connected = False
        logger.info("Disconnected from UDL")

    def ping(self) -> bool:
        """
        Check connection health

        Returns:
            bool: Connection alive status
        """
        if not self.connection:
            return False

        try:
            self.connection.process_data_events(time_limit=1)
            return self.connection.is_open
        except Exception:
            return False