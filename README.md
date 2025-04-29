# ManDaTor Energy

A distributed system for simulating and monitoring energy production and consumption within a smart energy community. Built using Python, Flask, PostgreSQL, Spring Boot, JavaFX, RabbitMQ, and Docker.

---

## System Overview

**Producer:** Simulates solar energy production.

**User:** Simulates household electricity usage.

**Usage Service:** Aggregates hourly usage and production data.

**Percentage Service:** Calculates grid dependency and internal consumption.

**PostgreSQL:** Persists all aggregated data.

**RabbitMQ:** Handles message-based communication between services.

## Quick Start

### Clone the repo:

```bash
git clone https://github.com/mweihmann/ManDaTor.git
cd ManDaTor
```

### After cloning the repository, copy the .env.example file and rename it to .env:

#### Windows in (Command Prompt)
```bash
copy .env.example .env
```

#### Windows (in PowerShell)
```bash
Copy-Item .env.example .env
```

#### macOS
```bash
cp .env.example .env
```

### Windows

1. Open PowerShell as Administrator
2. Run the startup script: `WINDOWS_START.ps1`

```powershell
./WINDOWS_START.ps1
```

---

### macOS

1. Open Terminal
2. Run the startup script:

```bash
chmod +x MACOS_START.sh
./MACOS_START.sh
```

---

## Service Endpoints
> All Endpoints start automatically

| Service             | Start Endpoint                                 | Stop Endpoint                                  | Description                             |
|---------------------|------------------------------------------------|------------------------------------------------|-----------------------------------------|
| **Producer 1**      | [http://localhost:5001/start](http://localhost:5001/start) | [http://localhost:5001/stop](http://localhost:5001/stop) | Starts/stops sending energy production        |
| **Producer 2**      | [http://localhost:5002/start](http://localhost:5002/start) | [http://localhost:5002/stop](http://localhost:5002/stop) | Starts/stops sending energy production        |
| **Producer 3**      | [http://localhost:5003/start](http://localhost:5003/start) | [http://localhost:5003/stop](http://localhost:5003/stop) | Starts/stops sending energy production        |
| **User 1**          | [http://localhost:5004/start](http://localhost:5004/start) | [http://localhost:5004/stop](http://localhost:5004/stop) | Starts/stops sending energy usage             |
| **User 2**          | [http://localhost:5005/start](http://localhost:5005/start) | [http://localhost:5005/stop](http://localhost:5005/stop) | Starts/stops sending energy usage             |
| **User 3**          | [http://localhost:5006/start](http://localhost:5006/start) | [http://localhost:5006/stop](http://localhost:5006/stop) | Starts/stops sending energy usage             |
| **Usage Service**   | [http://localhost:5007/start](http://localhost:5007/start) | [http://localhost:5007/stop](http://localhost:5007/stop) | Starts/stops listening and processing messages|
| **Percentage API**  | [http://localhost:5008/start](http://localhost:5008/start) | [http://localhost:5008/stop](http://localhost:5008/stop) | Starts/stops periodic percentage updates      |
| **RabbitMQ UI**     | [http://localhost:15672](http://localhost:15672)         | —                                              | Web interface to monitor messaging      |

---

## PostgreSQL – Command Reference

1. Find your database container ID using a terminal (also in Docker Desktop seeable)

```bash
docker ps
```

2. Look for the container with the image name postgres:alpine and enter the container’s interactive shell

```bash
docker exec -it <container_id> psql -U disysuser
```
> Replace `<container_id>` with your actual running database container ID

| Step | Description                            | Command                                                                 |
|------|----------------------------------------|-------------------------------------------------------------------------|
| 1    | Show all databases                     | `\l`                                                                    |
| 2    | Connect to the project database        | `\c mandator_energy_db`                                                |
| 3    | List all tables                        | `\dt`                                                                   |
| 4    | Show table schema for `usage_stats`    | `\d usage_stats`                                                       |
| 5    | Select all entries from `usage_stats`  | `SELECT * FROM usage_stats;`                                           |
| 6    | Quit the interface  | `\q`                                           |

---


## Reset the Project (if needed)
```bash
docker compose down -v
```
This removes **all data** including MySQL volumes.

---

## Project Purpose

This project was developed as part of the **Distributed Systems** course of the **Bachelor of Business Informatics** program  
at the **University of Applied Sciences Technikum Vienna**.

### Contributors

| Names               |
|--------------------|
| Manuel Weihmann    |
| Daniel Stepanovic  |
| Viktor Mandlbauer     |


# Docker setup for DISYS project
This Docker Compose configuration includes two essential containers for the project's infrastructure. The first container hosts the database, providing persistent storage and efficient management for the project's data. It ensures reliability and scalability, making it suitable for handling the application's data transactions. The second container is configured as a queue, which facilitates asynchronous task processing and communication between various components of the project. This setup improves system performance by decoupling workloads and enhancing the application's ability to handle concurrent operations. Together, these containers provide a robust and scalable foundation for the project's backend systems.

## Database
The database container in this setup runs a PostgreSQL database configured with a user named **"disysuser"** and a password **"disyspw"**. For the project, you will need to create the necessary databases and tables to store and manage the required data effectively. The connection details are as follows: the hostname is the localhost, the default port is 5432, and you can authenticate using the provided username and password. Ensure that the PostgreSQL container is running before attempting to connect.

## Queue 
The queue container in this setup runs a RabbitMQ Management instance, which provides both message queuing functionality and a user-friendly web-based management interface. RabbitMQ facilitates the communication between different components of the project by enabling reliable message passing. To connect to the RabbitMQ instance, you can access the management interface via a web browser by navigating to http://localhost:15672. By default, you can log in using the username "guest" and password "guest", unless overridden in the Docker Compose configuration. For programmatic access, RabbitMQ client libraries can connect using the host at localhost:5672. Ensure the container is running and accessible before attempting to connect.

docker exec -it <container_id> psql -U disysuser - connect to container
\l - Show all dbs
\c mandator_energy_db - select db
\dt - Show all tables
\d usage_stats - Shows columns and types
SELECT * FROM usage_stats; 