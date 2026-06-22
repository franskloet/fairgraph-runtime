# FAIRGraph Ingestion & Custom Schema Extension Guide

This guide explains how to create Excel data sheets matching standard schemas (such as the ISA-Tab metabolomics standard) while extending them dynamically with custom properties or classes. 

This demonstrates the core flexibility of the FAIRGraph platform: **combining established standards with dynamic schema extension**.

---

## 1. Structuring your Excel Workbook

FAIRGraph maps Excel sheets to **Classes** (entities) and columns to **Properties** (attributes or relationships). To set up your workbook:

1. **One Sheet per Class**: Create a tab for each class of data you want to import. For the ISATAB standard (`isatab_standard.yaml`), you would create tabs named:
   * `Investigations` (Target Class: `Investigation`)
   * `Studies` (Target Class: `Study`)
   * `Samples` (Target Class: `Sample`)
   * `Assays` (Target Class: `Assay`)
2. **The "Label" Column (Required)**: Every sheet must have a column named **`Label`** as the first column. This serves as the unique identifier for each record.
3. **Properties as Headers**: The remaining columns represent properties (fields).
4. **Linking Sheets**: To link a record to another tab, create a column named after the target class and input the exact `Label` of the record you want to link.

---

## 2. Implementing the ISATAB Standard

To match the `isatab_standard.yaml` template, structure your sheets with the standard property names. The Import Wizard will automatically recognize these headers and map them to their standardized URIs:

### Example Sheet Layout: `Investigations`
| Label | Identifier | Title | Description | Submission Date | Public Release Date | License |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| INV-2026-A | PROJ-098 | Lipidomics Study | Profiling blood serum | 2026-06-20 | 2026-12-01 | CC-BY-4.0 |

* *Under the hood mapping: `Title` maps to `dcterms:title`, `Submission Date` maps to `dcterms:dateSubmitted`, etc.*

### Example Sheet Layout: `Studies`
| Label | Identifier | Title | Description | Investigation |
| :--- | :--- | :--- | :--- | :--- |
| STUDY-01 | ST-992 | Serum Batch A | Metabolites analysis | **INV-2026-A** |

* *The `Investigation` column references the `Label` from the first sheet. FAIRGraph automatically creates a semantic link between the Study and the Investigation.*

---

## 3. Extending the Standard (Add Custom Properties)

You are **not limited** to the columns defined in the standard. If you need to capture extra metadata, simply append new columns to your sheets:

### Example: Adding Custom Fields
In your `Investigations` sheet, append columns like **`Funding Body`** or **`Lead PI`**:

| Label | Title | ... | Funding Body | Lead PI |
| :--- | :--- | :--- | :--- | :--- |
| INV-2026-A | Lipidomics Study | ... | **Horizon Europe** | **Dr. John Doe** |

### How the Import Wizard Resolves Custom Columns:
1. **Auto-Discovery**: During the mapping phase, the wizard notices `Funding Body` and `Lead PI` are not in the standard ISATAB schema.
2. **Automatic Schema Registration**: The wizard automatically registers these properties under the `custom:` namespace:
   * `Funding Body` $\rightarrow$ `custom:Funding_Body` (`https://fairgraph.nl/ontology/custom#Funding_Body`)
   * `Lead PI` $\rightarrow$ `custom:Lead_PI` (`https://fairgraph.nl/ontology/custom#Lead_PI`)
3. **Ontology Enrichment**: These properties are saved in the system vocabulary so they can be searched, filtered, and used in word clouds immediately.

---

## 4. Adding Entirely New Classes

If you want to model a concept that is not in the ISATAB standard at all (e.g. `Protocols` or `Instruments`), you do not need to rewrite the standard YAML file. You can do it directly in Excel:

1. **Create a New Tab**: Add a new tab named `Protocols` to your Excel workbook.
2. **Define Properties**:
   * Column A: `Label` (e.g., `PROTO-NMR-v1`)
   * Column B: `Identifier` (e.g., `P-NMR-01`)
   * Column C: `Title` (e.g., `NMR Extraction Protocol`)
   * Column D: `Description` (e.g., `Standard extraction using chloroform`)
   * Column E: `Protocol Type` (e.g., `Extraction`)
   * Column F: `Reagents` (e.g., `Methanol, Chloroform`)
3. **Reference the New Class**: In your `Assays` sheet, add a column named `Protocol` and reference `PROTO-NMR-v1`:

### Assays Tab
| Label | Identifier | Title | Description | Measurement Type | Technology Platform | Protocol |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ASSAY-01 | AS-772 | Liver Lipid Assay | Metabolomics assay of liver tissues | Metabolomics | Bruker NMR | **PROTO-NMR-v1** |

### How the Import Wizard Resolves New Tabs:
1. **Class Registration**: When you upload the workbook, the system identifies that `Protocols` is a new entity class.
2. **Interactive Mapping**: The wizard allows you to select the target class URI. You can choose an existing ontology class (like `schema:MedicalProcedure`) or let the system auto-register it as `custom:Protocol`.
3. **Semantic Linking**: Once approved, FAIRGraph automatically links the `Assay` to the new `Protocol` entity, checking any SHACL constraints and indexing them instantly.

---

## 5. Mandatory Core Metadata Fields & User-Scope Global Identifiers

To ensure clean indexing, semantic relationships, and validation, **every sheet in your Excel workbook must contain the following four mandatory columns**. If any of these columns are missing, the Import Wizard validation will report them as missing and block ingestion.

### The 4 Mandatory Columns & Their Usage

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

### Designing Reusable "User-Scope" Globals

By default, nested records in a workbook (like `Samples` or `Datasets`) have hierarchical composite keys (e.g. `study-a_sample-01`) to prevent clashes across studies. 

However, dictionary definitions such as **Manufacturers**, **Methods**, **Outcomes**, or **Instrumentations** are flat and globally reusable within your user namespace. These classes map to flat URIs (e.g. `https://fairgraph.nl/entity/{username}/{label_slug}`) regardless of parent fields, making them easy to link to across multiple uploads.

#### Suggested Strategy: Split Workbook Ingestion

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

## 6. Ingestion Modes: Strict vs. Flexible Ingestion

Depending on your database configuration, your instance may operate in **Strict Ingestion Mode** or **Flexible Ingestion Mode**. These modes enforce different levels of compliance with your registered standards (e.g., MIAPPE or ISATAB).

### Flexible Ingestion Mode (Default)
In Flexible Mode, you have the freedom to extend layouts dynamically:
* You can add custom columns (properties) to standard sheets, which are registered under the `custom:` namespace on the fly.
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


