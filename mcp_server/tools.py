import httpx
import os
import base64

# The base URL for the easy_automate API, configurable via environment variable
BASE_URL = os.environ.get("EASY_AUTOMATE_API_URL", "http://easy_automate:5000")

# --- Session Management Tools ---

def open_session(timeout: int = None):
    """Opens a new browser session via the easy_automate API."""
    try:
        with httpx.Client() as client:
            json_payload = {}
            if timeout is not None:
                json_payload['timeout'] = timeout
            response = client.post(f"{BASE_URL}/browser/open", json=json_payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}

def close_session(session_id: str):
    """Closes an existing browser session via the easy_automate API."""
    try:
        with httpx.Client() as client:
            response = client.post(f"{BASE_URL}/browser/{session_id}/close")
            response.raise_for_status()
            return {"status": "closed"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}

# --- Page CRUD Tools ---

def create_page(name: str, application_id: int, identifying_selectors: list, url: str = None, can_be_navigated_to: bool = False, interactive_selectors: list = None):
    """Creates a new page via the easy_automate API."""
    page_data = {
        'name': name,
        'application_id': application_id,
        'identifying_selectors': identifying_selectors,
        'url': url,
        'can_be_navigated_to': can_be_navigated_to,
        'interactive_selectors': interactive_selectors or []
    }
    try:
        with httpx.Client() as client:
            response = client.post(f"{BASE_URL}/pages", json=page_data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}

def get_page(id: int):
    """Retrieves a page by its ID via the easy_automate API."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/pages/{id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}

def list_pages():
    """Lists all pages via the easy_automate API."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/pages")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}

def update_page(id: int, name: str = None, url: str = None, can_be_navigated_to: bool = None, identifying_selectors: list = None, interactive_selectors: list = None):
    """Updates an existing page via the easy_automate API."""
    update_data = {}
    if name is not None:
        update_data['name'] = name
    if url is not None:
        update_data['url'] = url
    if can_be_navigated_to is not None:
        update_data['can_be_navigated_to'] = can_be_navigated_to
    if identifying_selectors is not None:
        update_data['identifying_selectors'] = identifying_selectors
    if interactive_selectors is not None:
        update_data['interactive_selectors'] = interactive_selectors

    try:
        with httpx.Client() as client:
            response = client.put(f"{BASE_URL}/pages/{id}", json=update_data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}

def delete_page(id: int):
    """Deletes a page via the easy_automate API."""
    try:
        with httpx.Client() as client:
            response = client.delete(f"{BASE_URL}/pages/{id}")
            response.raise_for_status()
            return {"status": "deleted"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}

# --- Browser Interaction Tools ---

def navigate_to_url(session_id: str, url: str):
    """Navigates to a specific URL in the given session via the easy_automate API."""
    try:
        with httpx.Client() as client:
            response = client.post(f"{BASE_URL}/browser/{session_id}/navigate_to_url", json={"url": url})
            response.raise_for_status()
            return {"status": "navigated"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}

def get_dom(session_id: str):
    """Retrieves the DOM of the current page via the easy_automate API."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/browser/{session_id}/dom")
            response.raise_for_status()
            return {"dom": response.text}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}

def get_screenshot(session_id: str):
    """Takes a screenshot of the current page via the easy_automate API."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/browser/{session_id}/screenshot")
            response.raise_for_status()
            screenshot_b64 = base64.b64encode(response.content).decode('utf-8')
            return {"screenshot": screenshot_b64}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}

def test_xpath(session_id: str, xpath: str):
    """Tests an XPath expression against the current page via the easy_automate API."""
    try:
        with httpx.Client() as client:
            response = client.post(f"{BASE_URL}/browser/{session_id}/test_xpath", json={"xpath": xpath})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}