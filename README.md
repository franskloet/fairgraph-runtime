# FAIR Graph Platform - Distributed Deployment

This directory contains the necessary Docker Compose configurations, metadata schemas, and sample data files to run the federated FAIR Graph platform without needing the source code.

The system launches:
- **Jena Fuseki Database Instances** (clinical, genomic, questionnaires, plant)
- **FAIR Graph API Instances** (for semantic queries, ingestion, and reasoning)
- **Central Routing Gateway** (coordinates federation, dynamic schema provisioning, and queries)
- **React Frontend Application** (Public Search, DB Browser, and Admin Panel)

---

## Prerequisites

1. **Docker & Docker Compose** (v2.0 or higher)
2. **Python 3.x** and `pip` (only required if you want to run the automated CLI ingestion script)
3. **Ollama** (for local LLM capabilities, see instructions below)

### Platform Compatibility (Intel/AMD vs. Apple Silicon M-Series)
- **Intel/AMD (x86_64/amd64):** All services run natively.
- **Apple Silicon (arm64/M-series macOS):** The API Gateway, Frontend, and individual database APIs run natively on ARM64 for peak performance. The Fuseki database services automatically run via Rosetta translation in Docker Desktop (forced via the `platform: linux/amd64` compose directive). No manual setup is required.

---

## 1. Installing Ollama & Loading the LLM

To run the application's semantic search and query parsing out of the box using a local, private LLM, you must install and run Ollama.

### A. Install Ollama
- **Linux:**
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- **macOS / Windows:**
  Download the installer from the [Ollama Official Website](https://ollama.com/).

### B. Pull the qwen2.5-coder Model
Once Ollama is installed and running, download the lightweight `qwen2.5-coder:1.5b` model:
```bash
ollama pull qwen2.5-coder:1.5b
```

---

## 2. Launching the Stack

1. **Check Environment Variables:**
   A pre-configured `.env` file is provided that hooks the containers into Ollama on your host system:
   ```env
   LLM_PROVIDER=ollama
   LLM_MODEL=qwen2.5-coder:1.5b
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   OLLAMA_MODEL=qwen2.5-coder:1.5b
   ```

2. **Start the Containers:**
   Start the services in detached mode:
   ```bash
   docker compose up -d
   ```
   *Note: On first run, Docker will pull the images (`frnzdock/...`) from Docker Hub.*

3. **Verify Health:**
   Wait about 30 seconds and check that all containers are healthy:
   ```bash
   docker compose ps
   ```

---

## 3. Ingesting Sample Data

You can upload the included sample datasets (under the `data/` directory) to the databases in two ways:

### Method A: Automated Ingestion Script (Recommended)
You can use the provided Python script to populate both the **clinical** and **genomic** databases automatically.

1. **Install requirements:**
   ```bash
   pip install requests
   ```
2. **Run the script:**
   ```bash
   python upload_all.py
   ```

### Method B: Upload via the Admin Panel UI
1. Open your browser and go to the Admin Panel: [http://localhost:3000/admin](http://localhost:3000/admin)
2. Log in using the default credentials:
   - **Username:** `admin`
   - **Password:** `admin-password`
3. Click on the **Ingestion Wizard / Upload** tool and select a database instance (e.g., `clinical` or `genomic`).
4. Upload a CSV file and its corresponding YAML metadata template from the `data/` directory (e.g., `data/clinical_projects.csv` alongside `data/yaml/clinical_projects.yaml`).
5. Complete the wizard steps to ingest the semantic graph.

---

## 4. Accessing the Platform

- **Public Semantic Search (Google-Style, Guest Access):**
  Open [http://localhost:3000/search](http://localhost:3000/search). Ask semantic questions like *"show clinical projects"* or *"find genomic samples"* to query datasets across databases.
- **Database Browser:**
  Open [http://localhost:3000/browse](http://localhost:3000/browse) to explore tables, columns, and records in detail.
- **Entity Detail Page:**
  Click on any search or browse result to view its attributes and visualize its semantic links in the interactive Cytoscape relationship graph.
- **Administrative Panel:**
  Open [http://localhost:3000/admin](http://localhost:3000/admin) to manage users, configure federated endpoints, register plugins, or provision completely new specialized database instances dynamically.
