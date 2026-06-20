# FAIR Graph Platform - User Manual

This manual provides deployment instructions, hardware resource requirements, and a detailed usage guide for the FAIR Graph platform.

---

## 1. Architecture Overview

The FAIR Graph platform is a federated metadata management system built on Semantic Web standards (RDF, SPARQL, SHACL). The deployment stack consists of:
1. **Frontend (React)**: Nginx-hosted static application offering search, tabular browsing, metadata ingestion wizards, and administrator tools.
2. **Central Router Gateway (FastAPI)**: Routes semantic queries to appropriate databases, coordinates OIDC security configurations, manages user registries, and handles dynamic database provisioning.
3. **Database Slice (Fuseki + API API)**:
   - **Jena Fuseki**: RDF Triple store executing SPARQL queries and validating SHACL constraints.
   - **FAIR Graph Instance API**: Translates REST actions into SPARQL updates, handles local file ingestion, and runs semantic reasoning.

The simplified deployment stack runs **one** active database: the **Questionnaires** database.

---

## 2. Hardware Resource Requirements

The resources required depend on the number of active database instances (slices) and whether you choose to host the Ollama Large Language Model (LLM) on the same machine.

### A. Resource Requirement Per Database Slice
Each database instance consists of a pair of containers: one **Fuseki DB** container and one **Instance API** container.
- **Jena Fuseki Container**:
  - **Memory (RAM)**: 500 MB base, 1 GB recommended (can peak to 2 GB under massive ingestion).
  - **CPU**: 0.2 vCPU base, up to 1-2 vCPUs under complex SPARQL query executions.
- **Instance API Container**:
  - **Memory (RAM)**: 200 MB base, 500 MB recommended.
  - **CPU**: 0.1 vCPU base, up to 1 vCPU under concurrent REST requests.
- **Slice Total**: **~700 MB RAM minimum (1.5 GB recommended)**, **0.3 vCPUs minimum**.

### B. Total Deployment Resource Requirements

#### Option 1: Standard 1-Database Stack (Questionnaires Only)
Runs Nginx Frontend, Central Router Gateway, Questionnaires Fuseki, and Questionnaires API.
- **Without Local LLM (Using remote API key or simple keywords)**:
  - **Memory (RAM)**: **~1.2 GB base, 2.5 GB recommended**.
  - **CPU**: **2 Cores (vCPUs) minimum**.
  - **Storage**: 10 GB of SSD storage (for Docker images and databases).
- **With Local LLM (Ollama hosting `qwen2.5-coder:1.5b`)**:
  - **Memory (RAM)**: **~3.5 GB base, 6 GB recommended**.
  - **CPU**: **4 Cores (vCPUs) with GPU acceleration** (Apple Metal/NVIDIA CUDA) or multi-core CPU.

#### Option 2: Scaled 4-Database Stack (Clinical, Genomic, Questionnaires, Plant)
If you decide to scale up the Compose file to include all 4 default databases.
- **Without Local LLM**:
  - **Memory (RAM)**: **~3.5 GB base, 6.5 GB recommended**.
  - **CPU**: **4 Cores (vCPUs) minimum**.
- **With Local LLM (Ollama hosting `qwen2.5-coder:1.5b`)**:
  - **Memory (RAM)**: **~6 GB base, 10 GB recommended**.
  - **CPU**: **6 - 8 Cores (vCPUs)**.

---

## 3. Installation & Deployment

### Step 1: Install Ollama (For Local Semantic Search)
To run query parsing locally using a private LLM:
1. **Install Ollama**:
   - **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`
   - **macOS / Windows**: Download from [ollama.com](https://ollama.com).
2. **Download Model**:
   ```bash
   ollama pull qwen2.5-coder:1.5b
   ```

### Step 2: Spin Up the Stack
1. Navigate to the `docker-setup` directory:
   ```bash
   cd docker-setup
   ```
2. Start the services:
   ```bash
   docker compose up -d
   ```
3. Check the status:
   ```bash
   docker compose ps
   ```
   Ensure all four services (`frontend`, `central_router`, `questionnaires_api`, and `questionnaires_fuseki_db`) are in the `healthy` status.

---

## 4. Usage Guide

- **Google-Style Semantic Search**: Navigate to [http://localhost:3000/search](http://localhost:3000/search) to issue natural language queries across the graph.
- **Database Browser**: Navigate to [http://localhost:3000/browse](http://localhost:3000/browse) to inspect ingested records. Click on any record to view its detail page and interact with the Cytoscape graph showing its relationships.
- **Vocabulary Explorer & Query Builder**: Navigate to [http://localhost:3000/wordcloud](http://localhost:3000/wordcloud) to explore terms. Clicking tags dynamically appends them as colored blocks to the query builder.
- **Admin Panel**: Navigate to [http://localhost:3000/admin](http://localhost:3000/admin) (credentials: `admin` / `admin`). Here you can manage databases, standards, groups, and user permissions.

---

## 5. Ingestion & Metadata Mapping (Questionnaires Example)

To load metadata into the platform, you must upload a **Standard Template** and then ingest **Tabular Data** mapped to that template.

### A. Register the Questionnaire Standard Schema
1. Go to **Admin Panel** -> **Manage Standards** tab.
2. Ensure the target database is set to `questionnaires`.
3. Select and upload [data/questionnaires_standard.yaml](file:///home/frans/Development/fair/fairgraph-2/docker-setup/data/questionnaires_standard.yaml).
4. Verify that the classes (e.g., `Project`, `Study`, `Outcome`, `Method`, `Dataset`) are displayed in the "Available Standards" section.

### B. Ingest Sample Data
1. Navigate to the **Import Wizard** page from the top navigation bar.
2. Select target database `questionnaires` and schema class `Project`.
3. Upload the sample data file [data/questionnaires_sample.csv](file:///home/frans/Development/fair/fairgraph-2/docker-setup/data/questionnaires_sample.csv) alongside its mapping file [data/questionnaires_sample.yaml](file:///home/frans/Development/fair/fairgraph-2/docker-setup/data/questionnaires_sample.yaml).
4. Follow the wizard steps to complete the ingestion. The records will now be visible in the search and browser pages!

---

## 6. Access Control & Visibility Levels

The system supports 4 visibility levels:
1. **Private**: Visible only to the owner.
2. **Group**: Visible to the owner and users belonging to the specific group.
3. **Extern (Federated)**: Visible to local logged-in users and external connections.
4. **Public (Local Anonymous)**: Visible to anyone, including guest users.

### Managing Groups & Databases
In the **Admin Panel** -> **Manage Users** tab:
- **Default Database Linkage**: Click the gear `⚙️` icon next to any group in the **Groups Directory** sidebar to configure its default databases.
- **Permissions Inheritance**: When adding a user to a group (e.g., `plants` linked to `plant` database), checking the group in the user details will automatically select and check the linked database checkbox in the user form.
