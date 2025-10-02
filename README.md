# Web Automation Backend

This project provides a powerful and flexible backend for a web automation application. Built with Python, Flask, and Selenium, it allows you to define and manage web applications and their pages via a REST API, and then interact with them programmatically.

## Features

-   **REST API:** A comprehensive API for managing applications, pages, and browser sessions.
-   **Database Integration:** Uses Flask-SQLAlchemy to store application and page definitions.
-   **Selenium Integration:** Leverages Selenium to control a web browser for automation tasks.
-   **Flexible Browser Management:** Supports both remote (Docker-based) and local browser execution.
-   **Interactive Mode:** Run the application with a visible browser for easy debugging and development.
-   **Containerized:** Comes with a `docker-compose.yml` file for easy setup and deployment.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   [Python 3.10+](https://www.python.org/downloads/)
-   [pip](https://pip.pypa.io/en/stable/installation/) (Python package installer)
-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

You can run the application in two ways: using Docker (recommended for a stable, containerized environment) or running it directly on your local machine (ideal for development and debugging).

### Method 1: Using Docker (Recommended)

This is the easiest way to get the application and its dependencies running.

1.  **Build and start the services:**
    ```bash
    docker compose up --build -d
    ```
    This command will build the Flask application image and start both the `web` and `selenium` services.

2.  **Access the application:**
    The API will be available at `http://localhost:5000`.

3.  **To stop the services:**
    ```bash
    docker compose down
    ```

### Method 2: Running Locally

This method allows you to run the application directly on your machine and see the browser in action.

1.  **Create a `.env` file:**
    Create a file named `.env` in the root of the project and add the following content:

    ```env
    # Flask configuration
    FLASK_APP=wsgi.py
    FLASK_RUN_HOST=0.0.0.0

    # Set to 'local' to use a local browser instance
    SELENIUM_MODE=local

    # Set to 'True' to see the browser UI when running locally
    INTERACTIVE_MODE=True

    # URL for the remote Selenium Hub (used if SELENIUM_MODE is 'remote')
    # SELENIUM_HUB_URL=http://selenium:4444/wd/hub
    ```

2.  **Initialize the database:**
    If you haven't run the application with Docker, you'll need to initialize the database and apply the migrations:
    ```bash
    export FLASK_APP=wsgi.py
    flask db upgrade
    ```

3.  **Run the Flask application:**
    ```bash
    flask run
    ```
    The API will be available at `http://localhost:5000`. When you open a new browser session via the API, a Chrome window will open on your desktop.

## API Overview

The application exposes the following API blueprints:

-   `/applications`: CRUD operations for managing web applications.
-   `/pages`: CRUD operations for managing pages within an application.
-   `/browser`: Endpoints for controlling the browser session (e.g., open, close, navigate, click, screenshot).
    -   `POST /browser/open`: Opens a new browser session. You can optionally provide a `timeout` in seconds in the JSON body. If no timeout is provided, the session will wait indefinitely for commands.
    -   `GET /browser/<session_id>/screenshot`: Returns a PNG image of the current browser view.
    -   `GET /browser/<session_id>/dom`: Returns the full HTML of the current page.