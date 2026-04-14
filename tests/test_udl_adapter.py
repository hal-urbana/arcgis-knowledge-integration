import pytest
from unittest.mock import MagicMock, patch
from automation.udl_adapter import UDLAdapter, UDLConfig, UDLMessage

def test_udl_config_initialization():
    config = UDLConfig(host="localhost", username="user", password="password")
    assert config.host == "localhost"
    assert config.username == "user"
    assert config.password == "password"
    assert config.port == 5672

def test_udl_adapter_initialization():
    config = UDLConfig(host="localhost")
    adapter = UDLAdapter(config)
    assert adapter.config == config
    assert adapter.connection is None
    assert adapter._is_connected is False

@patch('pika.BlockingConnection')
@patch('pika.PlainCredentials')
def test_udl_adapter_connect_success(mock_credentials, mock_connection):
    config = UDLConfig(host="localhost", username="user", password="password")
    adapter = UDLAdapter(config)
    
    # Mock connection and channel
    mock_conn_instance = MagicMock()
    mock_channel_instance = MagicMock()
    mock_connection.return_value = mock_conn_instance
    mock_conn_instance.channel.return_value = mock_channel_instance
    
    with patch.object(adapter, '_get_ssl_options', return_value={}):
        result = adapter.connect()
    
    assert result is True
    assert adapter.connection is not None
    assert adapter.channel is not None
