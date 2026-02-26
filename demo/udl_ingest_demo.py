"""
Demo: UDL to Esri Knowledge Ingest
Sample script showing how to use the ingest service
"""

import os
from automation.ingest_service import (
    create_ingest_service_from_config,
    IngestConfig,
    UDLConfig,
    IngestionStats
)


def example_basic_ingest():
    """
    Basic example of UDL ingestion setup
    """
    # Configuration - replace with your actual credentials
    config = {
        'udl_host': os.getenv('UDL_HOST', 'localhost'),
        'udl_topic': os.getenv('UDL_TOPIC', 'udl.some-topic'),
        'arcgis_url': os.getenv('ARCGIS_PORTAL_URL', 'https://your-portal.arcgis.com'),
        'arcgis_username': os.getenv('ARCGIS_USERNAME', 'your-username'),
        'arcgis_password': os.getenv('ARCGIS_PASSWORD', 'your-password'),
        'knowledge_graph_name': os.getenv('KG_NAME', 'UDL Demo Data')
    }

    print("=" * 60)
    print("UDL → Esri Knowledge Ingest Demo")
    print("=" * 60)

    # Create service
    print("\n1. Creating ingest service...")
    service = create_ingest_service_from_config(
        udl_host=config['udl_host'],
        udl_topic=config['udl_topic'],
        arcgis_url=config['arcgis_url'],
        arcgis_username=config['arcgis_username'],
        arcgis_password=config['arcgis_password'],
        knowledge_graph_name=config['knowledge_graph_name']
    )

    try:
        # Monitor ingestion
        while True:
            status = service.get_status()
            stats = status['statistics']

            print(f"\n📊 Ingestion Status:")
            print(f"   Running: {status['running']}")
            print(f"   Messages processed: {stats['total_messages']}")
            print(f"   Success: {stats['success_count']}")
            print(f"   Failures: {stats['fail_count']}")
            print(f"   Success Rate: {stats['success_rate']}%")
            print(f"   Batch Queue: {status['batch_queue_size']} items")

            # Keep running for demo purposes
            import time
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n\nStopping ingest service...")
        service.stop()
        print("Demo complete!")


def example_custom_config():
    """
    Example with custom configuration
    """
    print("\n" + "=" * 60)
    print("Custom Configuration Example")
    print("=" * 60)

    # Custom ingest config
    udl_config = UDLConfig(
        host=os.getenv('UDL_HOST', 'localhost'),
        port=5672,
        username=os.getenv('UDL_USERNAME', 'guest'),
        password=os.getenv('UDL_PASSWORD', 'guest'),
        virtual_host='/',
        ssl_verify=False  # Set to True in production
    )

    arcgis_config = {
        'portal_url': os.getenv('ARCGIS_PORTAL_URL'),
        'username': os.getenv('ARCGIS_USERNAME'),
        'password': os.getenv('ARCGIS_PASSWORD'),
        'verify_ssl': True
    }

    ingest_config = IngestConfig(
        udl_config=udl_config,
        arcgis_config=arcgis_config,
        topic=os.getenv('UDL_TOPIC', 'udl.some-topic'),
        max_retries=5,
        retry_delay=10,
        batch_size=20,
        max_backlog=500
    )

    service = create_ingest_service_from_config(
        udl_host=udl_config.host,
        udl_topic=ingest_config.topic,
        arcgis_url=arcgis_config['portal_url'],
        arcgis_username=arcgis_config['username'],
        arcgis_password=arcgis_config['password'],
        knowledge_graph_name="Custom Demo KG"
    )

    try:
        while True:
            status = service.get_status()
            print(f"\nProcessed: {status['statistics']['total_messages']}")
            import time
            time.sleep(5)

    except KeyboardInterrupt:
        service.stop()


def example_monitoring():
    """
    Example with focused monitoring
    """
    print("\n" + "=" * 60)
    print("Monitoring Example")
    print("=" * 60)

    service = create_ingest_service_from_config(
        udl_host=os.getenv('UDL_HOST', 'localhost'),
        udl_topic=os.getenv('UDL_TOPIC', 'udl.some-topic'),
        arcgis_url=os.getenv('ARCGIS_PORTAL_URL'),
        arcgis_username=os.getenv('ARCGIS_USERNAME'),
        arcgis_password=os.getenv('ARCGIS_PASSWORD')
    )

    try:
        # Run for first 60 seconds
        import time
        start_time = time.time()
        while time.time() - start_time < 60:
            status = service.get_status()
            stats = status['statistics']

            print(f"\rMessages: {stats['total_messages']} | "
                  f"Success: {stats['success_count']} | "
                  f"Rate: {stats['success_rate']}%", end='', flush=True)

            time.sleep(1)

    except KeyboardInterrupt:
        service.stop()


if __name__ == "__main__":
    import sys

    print("\nChoose an example:")
    print("1. Basic ingest (simple setup)")
    print("2. Custom configuration")
    print("3. Monitoring only")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        example_basic_ingest()
    elif choice == "2":
        example_custom_config()
    elif choice == "3":
        example_monitoring()
    else:
        print("Invalid choice. Running basic example...")
        example_basic_ingest()

    print("\nDone!")