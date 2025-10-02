# Web Automation Backend

This project provides a powerful and flexible backend for a web automation application, built with Python, Flask, and Selenium. It is composed of two main services: `easy_automate`, which provides a REST API for browser automation, and `mcp_server`, which exposes this functionality through the Model Context Protocol (MCP).

## Features

-   **REST API (`easy_automate`):** A comprehensive API for managing applications, pages, and browser sessions.
-   **MCP Server (`mcp_server`):** An MCP-compliant server that provides a standardized interface for AI tools to interact with the automation backend.
-   **Database Integration:** Uses Flask-SQLAlchemy to store application and page definitions.
-   **Selenium Integration:** Leverages Selenium to control a web browser for automation tasks.
-   **Flexible Browser Management:** Supports both remote (Docker-based) and local browser execution.
-   **Containerized:** Comes with a `docker-compose.yml` file for easy setup and deployment.

## Prerequisites

-   [Python 3.10+](https://www.python.org/downloads/)
-   [pip](https://pip.pypa.io/en/stable/installation/)
-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

## Local Setup and Installation

Follow these steps to set up and run the services locally for development and testing.

### 1. Set Up a Virtual Environment

First, create and activate a virtual environment to manage the project's dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

Install the required Python packages for both `easy_automate` and `mcp_server`:

```bash
pip install -r easy_automate/requirements.txt
pip install -r mcp_server/requirements.txt
```

### 3. Running `easy_automate`

The `easy_automate` service is a Flask application that provides the core browser automation functionality.

**a. Environment Configuration**

Create a `.env` file in the project root with the following content to run the browser in interactive mode on your local machine:

```env
# Flask configuration
FLASK_APP=easy_automate/src
FLASK_RUN_HOST=0.0.0.0

# Set to 'local' to use a local browser instance
SELENIUM_MODE=local

# Set to 'True' to see the browser UI when running locally
INTERACTIVE_MODE=True
```

**b. Database Initialization**

Initialize the database and apply migrations:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```
*Note: If you encounter errors, you may need to delete the `migrations` folder and the `easy_automate.db` file before running the commands.*

**c. Run the Service**

Start the `easy_automate` API server:

```bash
flask run
```

The API will be available at `http://localhost:5000`.

### 4. Running `mcp_server`

The `mcp_server` runs as a separate process and communicates with the `easy_automate` API.

**a. Environment Configuration**

The `mcp_server` will automatically connect to the `easy_automate` service at `http://easy_automate:5000`. If you are running `easy_automate` on a different host or port, set the `EASY_AUTOMATE_API_URL` environment variable:

```bash
export EASY_AUTOMATE_API_URL=http://localhost:5000
```

**b. Run the Service**

In a new terminal (with the virtual environment activated), start the `mcp_server`:

```bash
python mcp_server/main.py
```

The MCP server will start and listen for requests on stdio.

## Running with Docker (Recommended)

For a streamlined setup, you can use Docker Compose to run both services in a containerized environment.

1.  **Build and Start the Services:**
    ```bash
    docker-compose up --build -d
    ```
    This command will build the necessary Docker images and start the `easy_automate` and `selenium` services.

2.  **Access the API:**
    The `easy_automate` API will be available at `http://localhost:5000`.

3.  **Running the `mcp_server` with Docker:**
    To run the `mcp_server` and connect it to the containerized `easy_automate` service, execute the following command:
    ```bash
    docker-compose run mcp_server
    ```

4.  **Stopping the Services:**
    ```bash
    docker-compose down
    ```

## Testing

Both services come with their own test suites.

-   **Run `easy_automate` tests:**
    ```bash
    python -m pytest easy_automate/tests/
    ```

-   **Run `mcp_server` tests:**
    ```bash
    python -m pytest mcp_server/tests/
    ```