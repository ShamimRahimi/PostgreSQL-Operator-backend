# PostgreSQL Operator Project

This project automates the management of PostgreSQL instances in a Kubernetes cluster. It includes functionality for creating, resizing, and deleting Persistent Volume Claims (PVCs), managing PostgreSQL resources, and deploying the application via Docker.

## Features
- **PostgreSQL Management**: Deploy and manage PostgreSQL instances.
- **Persistent Volume Claims (PVCs)**: 
  - **Resizing PVCs**: Dynamically resize PVCs for your PostgreSQL database, ensuring that the new size is greater than the previous one.
  - **Deleting PVCs**: Safely delete PVCs when they are no longer needed.
- **Dockerized Application**: Easily install and run the project using Docker.
- **Dependency Management**: Install necessary Python dependencies via `requirements.txt`.

## Getting Started

### Prerequisites
Ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Kubernetes](https://kubernetes.io/docs/setup/) (minikube or a Kubernetes cluster)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)

### Installation

#### 1. Install PostgreSQL Operator
To deploy the PostgreSQL operator on your Kubernetes cluster:

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/your-repository.git
    cd your-repository
    ```

2. Install the project using the Docker file:
    ```bash
    docker build -t postgres-operator .
    docker run -d --name postgres-operator postgres-operator
    ```

#### 2. Install Project Requirements
You can install the Python dependencies using `requirements.txt`:
```bash
pip install -r requirements.txt
