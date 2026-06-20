# FAIR Graph Platform - Deployment Directory

This directory contains the configurations, metadata schemas, and sample files needed to deploy the FAIR Graph system in a production or sandbox environment.

### ⚠️ Lightweight Setup
To optimize resource consumption, the stack is configured to run **one** default database instance (**Questionnaires**) instead of the full four. This significantly lowers CPU and RAM overhead, making it ideal for standard server environments or local sandboxes.

---

## 1. Quick Start

1. **Prerequisites**: Ensure you have [Docker & Docker Compose](https://www.docker.com/) installed and running.
2. **Start the containers**:
   ```bash
   docker compose up -d
   ```
3. **Verify the services**:
   ```bash
   docker compose ps
   ```
   Ensure `frontend`, `central_router`, `questionnaires_api`, and `questionnaires_fuseki_db` containers are healthy.

---

## 2. Platform Documentation

For detailed information, please read the newly added manual:
- **[USER_MANUAL.md](file:///home/frans/Development/fair/fairgraph-2/docker-setup/USER_MANUAL.md)**: Contains hardware resource recommendations (per database slice and overall), system setup with Ollama for local LLM integration, user access levels, and data ingestion tutorials.

---

## 3. Sample Files Included

- **Vocabulary Schema**: `vocabulary/questionnaires_vocabulary.ttl`
- **Standard Template**: `data/questionnaires_standard.yaml`
- **Sample Metadata CSV**: `data/questionnaires_sample.csv`
- **Mapping Template**: `data/questionnaires_sample.yaml`
