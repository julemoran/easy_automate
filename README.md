# Web Automation Backend

This project provides a powerful and flexible backend for a web automation application. Built with Python, Flask, and Selenium and integrating Node-Red as a workflow tool, it allows you to define and manage web applications and their pages via a REST API, and then interact with them programmatically.

By that it implements in "supervised" automation that allows developers and process owners to efficiently collaborate, by developers to have an easy way to examine web pages and define possible interactions with a certain page to hand them over to the process owners which can orchestrate these interactions inside node red. A Headless Browser mode could also be used for "unsupervised" automation, where the whole browser interaction happens server side. However this is not the focus for the first version of the tool. 

## Features / Components

-   **REST API:** A comprehensive API for managing applications, pages, and browser sessions.
-   **EasyAutomate UI**: A UI that allows to interactively define applications and pages
-   **Database Integration:** Uses Flask-SQLAlchemy to store application and page definitions.
-   **Selenium Integration:** Leverages Selenium to control a web browser for automation tasks.
-   **Interactive Exploration:** Run the application with a visible browser for easy debugging and development of page definitions
-   **Node-Red based Workflow UI:** Define Events in the App - Run workflows automatically based on browser or APP interactions-

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   [Python 3.10+](https://www.python.org/downloads/)
-   [NodeJS 22.12+](https://nodejs.org/en)
-   [pip](https://pip.pypa.io/en/stable/installation/) (Python package installer, [uv] (https://github.com/astral-sh/uv) recommended)

Optional: 
-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create a virtual environment and activate it

    ```bash
    uv venv 
    .venv\scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

4. Make sure you have NodeJS installed, then install node-red by executing: 
    ```bash
    npm install -g node-red
    ```

5. Registering the custom nodes with node-red 

Go to the node red folder and register the custom nodes like this: 

```bash
pushd $HOME\.node-red 
npm install E:/easy_automate/node_red_node
```

where E:/easy_automate is the path where you checked out the repository. This will link the source code to the node red installation and make the custom nodes available in node-red. 

## Running the Application

The application consists of 3 components: 

- Flask Server (with embedded Frontend)
- Node RED
- Standalone Frontend (only for for development!)

### Initial Configuring the application 

Before running the application we need to create a configuration file. 

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
    If you haven't run the application, you'll need to initialize the database and apply the migrations:
    ```powershell
    # make sure you activate your python environment first with .venv\scripts\activate
    flask db init
    ```

    if you already ran the application you might need to update the DB: 

    ```bash    
    # make sure you activate your python environment first with .venv\scripts\activate
    flask db migrate
    flask db upgrade
    ```

### Running the application 

To run the flask backend you can do: 

```bash
flask run 
```

The UI will be available at `http://localhost:5000`. 

### Running Node RED 

Open a separate terminal and simply type: 

```bash
node-red 
```

It will open on http://localhost:1880 by default 

### Running the UI for development 

To run the UI go to the ./ui folder and run: 

```
npm install    # necessary only once
npm run dev 
```

## API Overview

The application exposes the following API blueprints:

-   `/api/applications`: CRUD operations for managing web applications.
-   `/api/pages`: CRUD operations for managing pages within an application.
-   `/api/browser`: Endpoints for controlling the browser session (e.g., open, close, navigate, click, screenshot).
    -   `POST /api/browser/open`: Opens a new browser session. You can optionally provide a `timeout` in seconds in the JSON body. If no timeout is provided, the session will wait indefinitely for commands.
    -   `GET /api/browser/<session_id>/screenshot`: Returns a PNG image of the current browser view.
    -   `GET /api/browser/<session_id>/dom`: Returns the full HTML of the current page.