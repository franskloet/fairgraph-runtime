# FAIRGraph Platform - Comprehensive Installation, Configuration & User Manual

This manual provides a complete, unified guide to deploying, configuring, using, and managing data ingestion on the FAIRGraph platform. 

---

## Table of Contents
1. [Introduction & Comparative Landscape](#1-introduction--comparative-landscape)
2. [Architecture & System Design](#2-architecture--system-design)
3. [Hardware Resource Requirements](#3-hardware-resource-requirements)
4. [Installation & Quick Start](#4-installation--quick-start)
5. [Remote Database Slice Deployment](#5-remote-database-slice-deployment)
6. [Data Ingestion & Excel Workbook Structuring](#6-data-ingestion--excel-workbook-structuring)
7. [Standards Implementation & Custom Schema Extension](#7-standards-implementation--custom-schema-extension)
8. [Ingestion Modes: Strict vs. Flexible Ingestion](#8-ingestion-modes-strict-vs-flexible-ingestion)
9. [User Access Control & Visibility Levels](#9-user-access-control--visibility-levels)
10. [Platform Usage Guide](#10-platform-usage-guide)
11. [Included Sample & Template Files](#11-included-sample--template-files)

---

## 1. Introduction & Comparative Landscape

Evaluating FAIRGraph against the landscape of semantic metadata management and FAIR (Findable, Accessible, Interoperable, Reusable) data tools, it sits at a unique intersection. It simplifies complex graph capabilities into an approachable "Semantic CMS."

### A. Comparison with Existing Solutions

* **FAIRDOM SEEK**:
  * *What it is*: The standard platform in the systems biology space for managing ISA-Tab metadata (investigations, studies, assays).
  * *How it compares*: SEEK is highly robust but structurally rigid. It relies on a traditional relational database (MySQL/Postgres) with RDF serialization on top. Adding custom properties dynamically or changing the ontology schema in SEEK is difficult and requires developer intervention.
  * *FAIRGraph's edge*: Excel is the schema builder. Because it uses a triplestore (Apache Jena Fuseki) natively, it embraces the **Open World Assumption**. Adding a custom column dynamically enriches the ontology (`custom:Property_Name`) without needing database migrations.

* **CEDAR Metadata Editor**:
  * *What it is*: A tool by the Stanford Center for Expanded Data Annotation and Retrieval that allows administrators to build forms (templates) based on BioPortal ontologies.
  * *How it compares*: CEDAR is excellent for metadata *authoring* and form schema design, but it functions purely as an editor outputting JSON-LD files rather than a queryable data registry or collaborative portal.
  * *FAIRGraph's edge*: It acts as both the **editor** (via interactive Excel imports) and the **active repository** (for browsing, knowledge graphs, search, and wordclouds).

* **COPO (Collaborative Open Plant Omics)**:
  * *What it is*: A metadata ingestion portal for omics datasets that aligns closely with standards like ISA and MIAPPE.
  * *How it compares*: COPO is excellent at publishing data to public repositories (like EBI), but it is heavily specialized for omics and does not support generic database federation or custom user-scope global registries.

* **Ontop / RML Mapper**:
  * *What they are*: Technical developer engines that translate relational databases, XML, or CSV files into RDF graphs using pre-defined mappings.
  * *How they compare*: These are purely developer-facing CLI utilities requiring complex RDF mapping files (in TTL or XML) with no UI, access control, or search features.
  * *FAIRGraph's edge*: The **Import Wizard** acts as a visual wrapper around semantic mapping. It auto-generates templates and mappings interactively so a researcher doesn't need to know what a URI or a SPARQL query is.

### B. Core Value Proposition ("Secret Sauce")
1. **Excel as a Schema-Generator**: meeting researchers where they already work by letting them use Excel tabs to declare classes, and columns to declare properties.
2. **Dynamic Schema Co-existence**: allowing a strict standard (e.g., `isatab_standard.yaml` or `miappe.yaml`) to seamlessly coexist with custom properties. If a user adds a `Funding Body` column, the system dynamically registers `custom:Funding_Body` and allows immediate search.
3. **Granular Security on Triple Stores**: Wrapping raw, multi-tenant RDF graphs with graph-level scoping, visibility toggles (`private`, `extern`, `public`), and user ownership overlays.
4. **LLM-Augmented Semantic Web**:
   - *SHACL Explainer*: Translating raw, complex SHACL validation reports into actionable markdown tips using a local LLM.
   - *NL-to-SPARQL Fallback*: Translating natural language questions to graph queries.
5. **Dynamic Server Federation**: Connecting independent nodes together via simple connection handshakes, OIDC tokens, and selective database sharing.

---

## 2. Architecture & System Design

The FAIRGraph platform is a federated metadata management system built on Semantic Web standards (RDF, SPARQL, SHACL). The deployment stack consists of three tiers:

```
[ Frontend (React/Nginx) ]
           │
           ▼
[ Central Router Gateway (FastAPI) ]
           │
     ┌─────┴───────────────┐
     ▼                     ▼
[ Database Slice A ]  [ Database Slice B ]
  ├── Instance API      ├── Instance API
  └── Jena Fuseki DB    └── Jena Fuseki DB
```

1. **Frontend (React)**: Nginx-hosted static application offering search, tabular browsing, metadata ingestion wizards, and administrator tools.
2. **Central Router Gateway (FastAPI)**: Routes semantic queries to appropriate databases, coordinates OIDC security configurations, manages user registries, and handles dynamic database provisioning.
3. **Database Slice (Fuseki + Instance API)**:
   - **Jena Fuseki**: RDF Triple store executing SPARQL queries and validating SHACL constraints.
   - **FAIR Graph Instance API**: Translates REST actions into SPARQL updates, handles local file ingestion, and runs semantic reasoning.

### Lightweight Deployment Setup
By default, the `docker-setup` directory is configured in a lightweight mode that spins up **one** active database slice (**Questionnaires**) instead of the full four. This significantly lowers CPU and RAM overhead, making it ideal for standard server environments or local sandboxes.

---

## 3. Hardware Resource Requirements

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
- **Without Local LLM**:
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

## 4. Installation & Quick Start

### Step 1: Install Ollama (For Local Semantic Search & SHACL Explanations)
To run query parsing and validation feedback locally using a private LLM:
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

## 5. Remote Database Slice Deployment

This setup details how to deploy specialized database instances (Jena Fuseki + specialized API) on a separate remote server (e.g. server with faster/larger storage) while keeping a single, centralized Central Router Gateway and Frontend stack.

### A. Network Architecture Layout
```
┌────────────────────────────────┐
│        Central Machine         │
│  [FE:3000] ──> [CentralRouter] │
└───────────────┬────────────────┘
                │ HTTP requests
                ▼
┌────────────────────────────────┐
│      Remote Storage Server     │
│   [Remote API:8080] ────────┐  │
│          │                  │  │
│          ▼ local SPARQL     │  │ JWT JWKS
│   [Remote Fuseki:3030]      └──┼─> [CentralRouter]
└────────────────────────────────┘
```

### B. Deployment Steps

#### Step 1: Deploy Database Slice on the Remote Server
On the remote server that holds the fast/large storage:
1. Create a workspace directory (e.g. `fairgraph-slice`).
2. Save the following minimal `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  clinical_fuseki:
    image: frnzdock/fairgraph-fuseki:latest
    container_name: clinical_fuseki_db
    ports:
      - "3030:3030" # Optional: allows local SPARQL inspection on remote server
    volumes:
      - clinical_fuseki-data:/fuseki
    command: [ "/jena-fuseki/fuseki-server", "--mem", "/ds" ]
    healthcheck:
      test: [ "CMD-SHELL", "wget --no-verbose --tries=1 --spider http://127.0.0.1:3030/ || exit 1" ]
      interval: 10s
      timeout: 3s
      retries: 30

  clinical_api:
    image: frnzdock/fairgraph-api:latest
    container_name: clinical_api
    ports:
      - "8080:8000" # Expose the API port to your network
    environment:
      - FUSEKI_BASE_URL=http://clinical_fuseki:3030/ds
      - ADMIN_PASSWORD=admin
      - VOCAB_PATH=./vocabulary/clinical_vocabulary.ttl
      - AUTH_MODE=oidc
      # CRITICAL: Point validation requests back to the Central Router Gateway IP
      - OIDC_JWKS_URL=http://<YOUR-CENTRAL-ROUTER-IP>:8000/.well-known/jwks.json
      - OIDC_ISSUER_URL=http://localhost:8000
    depends_on:
      clinical_fuseki:
        condition: service_healthy

volumes:
  clinical_fuseki-data:
```

3. Replace `<YOUR-CENTRAL-ROUTER-IP>` with the public or private LAN IP address of the machine hosting the Central Router.
4. Run: `docker compose up -d`

#### Step 2: Configure the Central Router Gateway
On the primary machine hosting your Central Router and Frontend:
1. Open your Central Router `.env` file (or docker-compose file) and modify the clinical instance environment mapping to point to the remote server IP:
   ```env
   INSTANCE_CLINICAL_URL=http://<REMOTE-SERVER-IP>:8080
   ```
2. Restart the local central router service to pick up the changes:
   ```bash
   docker compose up -d central_router
   ```

#### Step 3: Verification
1. Access the local browser UI on `http://localhost:3000`.
2. Go to the **Import Wizard** page and ingest a sample template and CSV dataset targeting the clinical instance.
3. Verify that the triples are successfully written to the remote Fuseki database volume.

---

## 6. Data Ingestion & Excel Workbook Structuring

FAIRGraph maps Excel sheets to **Classes** (entities) and columns to **Properties** (attributes or relationships).

### A. Workbook Structuring Rules
1. **One Sheet per Class**: Create a tab for each class of data you want to import. For the ISATAB standard (`isatab_standard.yaml`), you would create tabs named:
   * `Investigations` (Target Class: `Investigation`)
   * `Studies` (Target Class: `Study`)
   * `Samples` (Target Class: `Sample`)
   * `Assays` (Target Class: `Assay`)
2. **Properties as Headers**: The remaining columns represent properties.
3. **Linking Sheets**: To link a record to another tab, create a column named after the target class and input the exact `Label` of the record you want to link.

---

### B. The 4 Mandatory Columns & Their Usage

To ensure clean indexing, semantic relationships, and validation, **every sheet in your Excel workbook must contain the following four mandatory columns**. If any of these columns are missing, the Import Wizard validation will report them as missing and block ingestion.

1. **`Label`** (Semantic Mapping: `rdfs:label`)
   - **Function & Behavior**: The primary human-readable display name for the entity.
   - **Usage**: It is shown in search results, browsing lists, and entity cards. In the background, it is used to generate the database URI slug (the unique URL suffix) and is the default key used to reference this record from other tabs *within the same workbook*.
   
2. **`Identifier`** (Semantic Mapping: `dcterms:identifier`)
   - **Function & Behavior**: A unique, machine-readable key (e.g., `outcome_ID_sweetness-preference` or `study_ID_batch-2`).
   - **Usage**: Ensures global reusability. Once ingested, this identifier is cached. Subsequent workbook uploads can refer to this unique ID to automatically link to the existing record without duplicating it in the database.

3. **`Title`** (Semantic Mapping: `dcterms:title`)
   - **Function & Behavior**: The formal or official title of the record.
   - **Usage**: Captures formal names (e.g., "Lipidomics Study of Blood Serum" or "Standard NMR Extraction Protocol"). Used for cataloging and formal metadata headers.

4. **`Description`** (Semantic Mapping: `rdfs:comment`)
   - **Function & Behavior**: A textual description or summary.
   - **Usage**: Documents definitions, notes, experimental conditions, or other relevant text. This field is fully indexed for search queries.

---

### C. Designing Reusable "User-Scope" Globals
By default, nested records in a workbook (like `Samples` or `Datasets`) have hierarchical composite keys (e.g. `study-a_sample-01`) to prevent clashes across studies. 

However, dictionary definitions such as **Manufacturers**, **Methods**, **Outcomes**, or **Instrumentations** are flat and globally reusable within your user namespace. These classes map to flat URIs (e.g. `https://fairgraph.nl/entity/{username}/{label_slug}`) regardless of parent fields, making them easy to link to across multiple uploads.

#### Strategy: Split Workbook Ingestion
To keep your main workbooks clean, you can manage frequently returning dictionary items in a separate definitions file:

1. **Step 1: Upload Globals (`Q1.xlsx`)**
   Create a workbook containing tabs for your definitions (e.g. `Manufacturers` or `Outcomes`). Assign clear, unique values in the **`Identifier`** column:
   
   **`Outcomes` Tab in Q1.xlsx**
   | Label | Identifier | Title | Description |
   | :--- | :--- | :--- | :--- |
   | Sweetness Preference | outcome_ID_sweetness-preference | Sweetness Preference Outcome | Assessment of high-sweetness choice |

   Upload `Q1.xlsx`. This registers `https://fairgraph.nl/entity/{username}/sweetness_preference` in your database.

2. **Step 2: Link in Subsequent Uploads (`Q2.xlsx`)**
   When creating your study workbook (`Q2.xlsx`), you don't need to redefine the outcomes. Simply add the relationship column and use the registered **`Identifier`** value as the reference:

   **`Studies` Tab in Q2.xlsx**
   | Label | Identifier | Title | Outcome |
   | :--- | :--- | :--- | :--- |
   | Study B | ST-B99 | Clinical Study B | **outcome_ID_sweetness-preference** |

When you upload `Q2.xlsx`, FAIRGraph's smart reference resolver queries your database cache, locates the pre-existing global identifier, and automatically links Study B to the existing `Sweetness Preference` entity!

---

## 7. Standards Implementation & Custom Schema Extension

You can extend standards dynamically without altering the standard configuration schema files.

### A. Implementing a Standard (e.g. ISATAB)
Structure your Excel tabs and columns to match the properties defined in the standard. For example, in an `Investigations` tab:

| Label | Identifier | Title | Description | Submission Date | Public Release Date | License |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| INV-2026-A | PROJ-098 | Lipidomics Study | Profiling blood serum | 2026-06-20 | 2026-12-01 | CC-BY-4.0 |

The Import Wizard maps `Title` to `dcterms:title`, `Submission Date` to `dcterms:dateSubmitted`, etc., automatically.

### B. Adding Custom Fields (Properties)
Append extra columns to your sheets (e.g., `Funding Body` or `Lead PI` in `Investigations`). 
1. **Auto-Discovery**: The wizard notices these are not in the standard ISATAB schema.
2. **Auto-Registration**: The wizard registers them under the `custom:` namespace:
   * `Funding Body` $\rightarrow$ `custom:Funding_Body` (`https://fairgraph.nl/ontology/custom#Funding_Body`)
   * `Lead PI` $\rightarrow$ `custom:Lead_PI` (`https://fairgraph.nl/ontology/custom#Lead_PI`)
3. **Ontology Enrichment**: They are saved in the database vocabulary and are instantly searchable.

### C. Adding Entirely New Classes (Tabs)
Add a new tab, such as `Protocols`.
1. **Define Properties**: Column headers `Label`, `Identifier`, `Title`, `Description`, and custom properties like `Protocol Type` or `Reagents`.
2. **Reference the Class**: In another sheet (e.g. `Assays`), reference the `Label` of a protocol (e.g. `PROTO-NMR-v1`).
3. **Interactive Mapping**: The system identifies that `Protocols` is a new entity class and asks you to select its class URI. You can choose a class from public ontologies or let the system auto-register it as `custom:Protocol`.

---

## 8. Ingestion Modes: Strict vs. Flexible Ingestion

Depending on your database configuration, your instance may operate in **Strict Ingestion Mode** or **Flexible Ingestion Mode**. These modes enforce different levels of compliance with your registered standards.

### Flexible Ingestion Mode (Default)
In Flexible Mode, you have the freedom to extend layouts dynamically:
* You can add custom columns (properties) to standard sheets. They are registered under the `custom:` namespace on the fly.
* You can define entirely new tabs (classes) without pre-declaring them.
* Properties can be mapped dynamically during ingestion regardless of where they are defined in the standard.

### Strict Ingestion Mode
Strict Mode enforces consistency and compliance with your schemas. When Strict Mode is enabled:
1. **Registered Classes Only**: You can only map Excel tabs to classes that are explicitly defined in your standard templates.
2. **Class-Specific Properties**: You can only map columns to properties that are **explicitly defined for that specific class** in the standard schema.
   * *Example*: If the standard defines `hasIdentifier` under the `Study` class but not under the `Investigation` class, mapping a column on an `Investigations` sheet to `hasIdentifier` **will fail** with a validation error:
     `Strict validation failed: Property '...' is not defined for class 'Investigation' in the standards.`
   * If you need a property to be available on multiple classes, it must be explicitly defined under each class's properties list in your standard YAML schema template.
3. **Core Metadata Exceptions**: Standard metadata properties (`rdfs:label`, `dcterms:identifier`, `dcterms:title`, `rdfs:comment`, and `fs:sharedWith`) are always allowed on all classes in both modes.

---

## 9. User Access Control & Visibility Levels

The system supports 4 visibility levels:
1. **Private**: Visible only to the owner.
2. **Group**: Visible to the owner and users belonging to the specific group.
3. **Extern (Federated)**: Visible to local logged-in users and external connections.
4. **Public (Local Anonymous)**: Visible to anyone, including guest users.

### Managing Groups & Databases
In the **Admin Panel** -> **Manage Users** tab:
- **Default Database Linkage**: Click the gear `⚙️` icon next to any group in the **Groups Directory** sidebar to configure its default databases.
- **Permissions Inheritance**: When adding a user to a group (e.g., `plants` linked to `plant` database), checking the group in the user details will automatically select and check the linked database checkbox in the user form.

---

## 10. Platform Usage Guide

- **Google-Style Semantic Search**: Navigate to [http://localhost:3000/search](http://localhost:3000/search) to issue natural language queries across the graph.
- **Database Browser**: Navigate to [http://localhost:3000/browse](http://localhost:3000/browse) to inspect ingested records. Click on any record to view its detail page and interact with the Cytoscape graph showing its relationships.
- **Vocabulary Explorer & Query Builder**: Navigate to [http://localhost:3000/wordcloud](http://localhost:3000/wordcloud) to explore terms. Clicking tags dynamically appends them as colored blocks to the query builder.
- **Admin Panel**: Navigate to [http://localhost:3000/admin](http://localhost:3000/admin) (credentials: `admin` / `admin-password`). Here you can manage databases, standards, groups, and user permissions.

---

## 11. Included Sample & Template Files

Inside the `docker-setup` directory:
- **Vocabulary Schema**: `vocabulary/questionnaires_vocabulary.ttl`
- **Standard Template**: `data/questionnaires_standard.yaml`
- **Sample Metadata CSV**: `data/questionnaires_sample.csv`
- **Mapping Template**: `data/questionnaires_sample.yaml`
