# Project Name

## Overview
This project uses a Makefile to streamline environment setup and management
for development, backend, and DB environments.<br> 
Below are the available `make` commands and their usage instructions.

## Prerequisites
- Ensure you have `make` installed on your system.
- Ensure you have `docker` installed and ***RUNNING*** on your system.

## Setup
Before running any of the commands, ensure you have the required `.env` file in the `deployment` directory (if applicable).<br> 
The Makefile will automatically include it if present.

## Usage
### Deployment Commands

#### Run Linters
- Isort
- Ruff
- Flake8  
Settings avaliable at ./backend/pyproject.toml
  ```bash
  make format-all
  ```

### Run security checks
- Bandit
- Semgrep  
Settings avaliable at ./backend/pyproject.toml
  ```bash
  make security-all
  ```


#### Development Environment

- **Start Development Environment**  
  Now `backend` and `postgres-db` containers are running.  
  `backend` container is available at `localhost:8765`  
  `postgres-db` container is available at `localhost:5432`  
  To start the development environment:<br>
  ```bash
  make up-dev
  ```
  

- **Stop Development Environment**  
  To stop the development environment:
  ```bash
  make down-dev
  ```

- **Stop Development Environment and Remove Volumes**  
  ***IMPORTANT:*** Removing volumes is not equal to removing persistent data on local storage.  
  To stop the development environment and remove associated volumes:
  ```bash
  make down-dev-volumes
  ```

#### Backend Environment

- **Start Backend Environment**  
  To start the backend environment:

  ```bash
  make up-backend
  ```

#### DB Environment

- **Start Postgres Environment**  
  To start the postgres environment:

  ```bash
  make up-db
  ```
  
- **Stop Postgres Environment**  
  To start the postgres environment:

  ```bash
  make down-dev
  ```


## Notes  
- Commands are executed from the `main` directory. Ensure all necessary scripts are present in this directory.
- Modify the `deployment/.env` file as needed to configure environment variables.
- The `PROJDIR` variable in the Makefile ensures commands are executed relative to the project root.

## Troubleshooting
- If any command fails, check the `deployment` directory for detailed logs or errors.
- Ensure all required dependencies for the `deployment` scripts are installed.

## Usage
```bash
  make up-dev
```
Swagger docs available at `0.0.0.0:8765/api/docs`
Docs are interactive with plethora of usable examples to choose from.  
Input, output and exceptions schemas are available.

To connect to DB directly use: `postgresql://localhost:5432/postgres`  
User: `postgres`, Password:`postgres`  
```bash
  make down-dev
```

## TBD
- Internal exceptions
- Exceptions model to streamline HTTPExceptions
- Loki Grafana
- Prometheus