import pytest
from unittest.mock import MagicMock
import httpx
import base64

# Add the parent directory to the sys.path to allow imports from mcp_server
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools import (
    open_session, close_session, create_page, get_page, list_pages,
    update_page, delete_page, navigate_to_url, get_dom, get_screenshot, check_xpath_existence
)

BASE_URL = "http://easy_automate:5000"

@pytest.fixture
def mock_httpx_client(mocker):
    """Fixture to mock httpx.Client."""
    mock_client_instance = MagicMock(spec=httpx.Client)

    # Make the mock instance a context manager
    mock_client_context_manager = MagicMock()
    mock_client_context_manager.__enter__.return_value = mock_client_instance
    mock_client_context_manager.__exit__.return_value = None

    mocker.patch('httpx.Client', return_value=mock_client_context_manager)

    return mock_client_instance

def test_open_session_success(mock_httpx_client):
    """Test successful session opening."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"session_id": "test_session_123"}
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    result = open_session(timeout=60)

    mock_httpx_client.post.assert_called_once_with(f"{BASE_URL}/browser/open", json={'timeout': 60}, timeout=60)
    assert result == {"session_id": "test_session_123"}

def test_open_session_no_timeout(mock_httpx_client):
    """Test successful session opening without a timeout."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"session_id": "test_session_123"}
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    result = open_session()

    mock_httpx_client.post.assert_called_once_with(f"{BASE_URL}/browser/open", json={}, timeout=None)
    assert result == {"session_id": "test_session_123"}

def test_close_session_success(mock_httpx_client):
    """Test successful session closing."""
    session_id = "test_session_123"
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    result = close_session(session_id)

    mock_httpx_client.post.assert_called_once_with(f"{BASE_URL}/browser/{session_id}/close")
    assert result == {"status": "closed"}

def test_get_screenshot_success(mock_httpx_client):
    """Test successful screenshot retrieval."""
    session_id = "test_session_123"
    mock_image_data = b'fake_image_bytes'
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.content = mock_image_data
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.get.return_value = mock_response

    result = get_screenshot(session_id)

    mock_httpx_client.get.assert_called_once_with(f"{BASE_URL}/browser/{session_id}/screenshot")

    expected_b64 = base64.b64encode(mock_image_data).decode('utf-8')
    assert result == {"screenshot": expected_b64}

def test_http_error(mock_httpx_client):
    """Test handling of HTTPStatusError."""
    session_id = "test_session_123"
    mock_request = MagicMock(spec=httpx.Request)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.request = mock_request

    http_error = httpx.HTTPStatusError(
        "Not Found", request=mock_request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_httpx_client.post.return_value = mock_response

    result = close_session(session_id)

    assert "error" in result
    assert "HTTP error occurred: 404" in result["error"]
    assert "Not Found" in result["details"]

def test_request_error(mock_httpx_client):
    """Test handling of RequestError."""
    session_id = "test_session_123"
    mock_request = MagicMock(spec=httpx.Request)
    mock_request.url = "http://fakeurl"

    request_error = httpx.RequestError(
        "Connection failed", request=mock_request
    )
    mock_httpx_client.post.side_effect = request_error

    result = close_session(session_id)

    assert "error" in result
    assert "An error occurred while requesting" in result["error"]

def test_check_xpath_existence(mock_httpx_client):
    """Test successful xpath check."""
    session_id = "test_session_123"
    xpath = "//div"
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"found": True}
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    result = check_xpath_existence(session_id, xpath)

    mock_httpx_client.post.assert_called_once_with(f"{BASE_URL}/browser/{session_id}/test_xpath", json={"xpath": xpath})
    assert result == {"found": True}