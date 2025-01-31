# Note: This work is in progress

# New Backend server for our Admin site/remote server

## Prerequisites

- Python 3.13 or newer
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

1. CD into the backend folder.

2. Setup a virtual enivronment: 

    ```sh
    uv venv
    source .venv/Scripts/activate  # On Linux/Mac use `.venv\bin\activate`
    ```

3. Install dependencies for the project:

    ```sh
    uv sync
    ```
    
## Running the server

1. Run the application:

    ```sh
    uv run run_app.py
    ```
    
2. The server will be running at 'http://127.0.0.1:8000'.

## API/Schema Documentation

- You can view the FastAPI documentation by navigating to `http://127.0.0.1:8000/docs` in your web browser while the server is running.