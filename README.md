# KYC/AML Industry Demo

[![Databricks](https://img.shields.io/badge/Databricks-Solution_Accelerator-FF3621?style=for-the-badge&logo=databricks)](https://databricks.com)
[![Unity Catalog](https://img.shields.io/badge/Unity_Catalog-Enabled-00A1C9?style=for-the-badge)](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
[![Serverless](https://img.shields.io/badge/Serverless-Compute-00C851?style=for-the-badge)](https://docs.databricks.com/en/compute/serverless.html)

An end-to-end **Know Your Customer / Anti-Money Laundering** demo built on Databricks. It covers AI-powered customer onboarding, real-time transaction screening with ML, and a Chief Compliance Officer dashboard — all wired together with Unity Catalog, Databricks Apps, and Lakeflow.

## Why Databricks?

Financial institutions typically stitch together 5–10 separate tools for KYC compliance: document OCR, screening databases, ML fraud models, streaming infrastructure, BI dashboards, and case management. Each integration adds latency, cost, and regulatory risk.

Databricks replaces this patchwork with **one governed platform**:

- **Faster onboarding** — AI-powered document parsing and real-time screening reduce customer onboarding from days to minutes.
- **Continuous compliance** — Streaming pipelines score every transaction as it arrives, replacing batch-overnight processes that let suspicious activity slip through.
- **Lower operational cost** — One platform, one governance model (Unity Catalog), one deployment (Asset Bundles). No glue code between siloed tools.
- **Audit-ready** — Every data lineage, model version, and screening decision is tracked in Unity Catalog, simplifying regulatory audits.

This demo shows the complete journey — from a customer uploading a passport to the CCO reviewing compliance KPIs — all on Databricks.

## What it demonstrates

| Capability | How it's used |
|------------|---------------|
| **SQL AI functions** | `ai_parse_document` and `ai_extract` parse passport and utility bill images into structured fields |
| **Unity Catalog functions** | `check_pep`, `check_sanctions`, `check_fraud`, `check_customer_risk` — fuzzy-match screening against demo tables |
| **LangChain agent** | Orchestrates the KYC conversation flow with tool calling on a Foundation Model (Llama 3.3 70B) |
| **Databricks Apps** | Agent deployed as a standalone app + 6-scene interactive frontend |
| **Lakebase** | Managed PostgreSQL backing LangGraph checkpointing for persistent conversation memory |
| **ML Pipeline** | scikit-learn fraud/risk classifier registered in Unity Catalog, served via MLflow |
| **Streaming** | Zerobus Ingest feeds real-time SEPA transactions into a Delta Live Tables pipeline (bronze -> silver -> gold) |
| **AI/BI Dashboards** | CCO compliance dashboard with Genie Space for natural language exploration |

## Architecture

| Layer | Component | Key Tech |
|-------|-----------|----------|
| **Frontend** | 6-scene interactive app | Databricks Apps, HTML/JS |
| **Agents** | KYC onboarding agent (Scene 1) | LangChain, UC Functions, Lakebase, Databricks Apps |
| **ML** | SEPA fraud/risk classifier (Scene 2) | scikit-learn, MLflow, Unity Catalog Models |
| **Streaming** | Real-time transaction pipeline (Scene 2) | Zerobus Ingest, Delta Live Tables |
| **Data** | Unity Catalog tables, volumes, functions | Delta Lake, UC |
| **Dashboards** | CCO compliance dashboard (Scene 6) | AI/BI Dashboards, Genie Spaces |

## Installation Guidelines

1. Clone the project into your Databricks Workspace
2. Open the Asset Bundle Editor in the Databricks UI
3. Click on "Deploy"

### CLI Deployment

```bash
# Configure CLI with your workspace
databricks bundle deploy --target dev
```

This syncs notebooks, pipelines, agent source, and the frontend app to the workspace and deploys the DLT pipeline.

**Override variables** at deploy time:

```bash
databricks bundle deploy --target dev --var="catalog=my_catalog" --var="schema=my_schema"
```

## Prerequisites

- **Databricks workspace** with Unity Catalog enabled
- **Configure [`notebooks/_shared/config`](notebooks/_shared/config.py)** — set your catalog, schema, table name, and pipeline name before running notebooks
- **Catalog permissions:** ability to create schemas and tables in the configured catalog
- **(Scene 2)** Zerobus Ingest enabled + service principal with MODIFY/SELECT on the target table
- **(Scene 1 deploy)** SQL warehouse ID for the Statement Execution API

## Configuration

All demo settings live in **[`notebooks/_shared/config.py`](notebooks/_shared/config.py)**. Edit the four variables at the top:

```python
CATALOG         = "main"
SCHEMA          = "kyc_demo"
SEPA_TABLE_NAME = "sepa_transactions"
PIPELINE_NAME   = "SEPA KYC Demo Pipeline"
```

All notebooks pick this up via `%run ../_shared/config`. When run as a job task, `databricks.yml` variables override automatically.

## Scenes

### Scene 1: KYC Onboarding (AI Agent)

A conversational agent walks a customer through onboarding: identity verification (passport parsing via `ai_parse_document`), proof of address, PEP/sanctions/fraud screening, SBI risk check, and account creation.

| # | Notebook | Purpose |
|---|----------|---------|
| 1 | [`01_kyc_data_setup`](notebooks/scene1_kyc_onboarding/01_kyc_data_setup.ipynb) | Create schema, seed tables (PEP, sanctions, fraud, SBI codes), and UC functions |
| 2 | [`02_kyc_agent`](notebooks/scene1_kyc_onboarding/02_kyc_agent.ipynb) | Run the KYC agent interactively in the notebook |
| 3 | [`03_kyc_agent_deploy`](notebooks/scene1_kyc_onboarding/03_kyc_agent_deploy.ipynb) | Deploy the agent as a Databricks App with Lakebase memory |

**Run order:** `01` (once) -> `02` (interactive demo) or `03` (deploy as app)

### Scene 2: Transaction Screening (ML + Streaming)

Train a fraud/risk ML model on SEPA transactions, deploy a DLT streaming pipeline, and ingest real-time data via Zerobus. Transactions flow through bronze -> silver (ML risk scoring) -> gold layers.

| # | Notebook | Purpose |
|---|----------|---------|
| 1 | [`01_train_model_and_pipeline`](notebooks/scene2_txn_screening/01_train_model_and_pipeline.ipynb) | Generate training data, train classifier, register model in UC, create SEPA source table, link DLT pipeline |
| 2 | [`02_zerobus_ingest`](notebooks/scene2_txn_screening/02_zerobus_ingest.ipynb) | Stream SEPA transactions into the source table via Zerobus Ingest |

**Run order:** `01` (train + pipeline) -> `02` (ingest)

**Zerobus credentials:** Notebook `02` needs `client_id` and `client_secret` for a service principal. Enter them in the widgets when running interactively, or use a secret scope.

### Scenes 3-5: AI Monitoring, EDD Investigation, SAR Filing

Frontend-only scenes (no notebooks required). Part of the interactive app deployed via `databricks.yml`.

### Scene 6: CCO Dashboard

| # | Notebook | Purpose |
|---|----------|---------|
| 1 | [`01_generate_dashboard_data`](notebooks/scene6_cco_dashboard/01_generate_dashboard_data.py) | Generate compliance metrics and KPI summary tables |

After generating data, create an AI/BI Dashboard or Genie Space on top of these tables.

## Project structure

```
pkyc/
├── databricks.yml                          # Asset bundle config (pipeline, app, variables)
├── notebooks/
│   ├── 00_overview.ipynb                   # Full demo walkthrough and links
│   ├── _shared/
│   │   ├── config.py                       # Edit this: catalog, schema, table names
│   │   └── sepa_constants.py               # SEPA domain data (companies, locations, currencies)
│   ├── scene1_kyc_onboarding/
│   │   ├── 01_kyc_data_setup.ipynb         # Schema, tables, UC functions, volume assets
│   │   ├── 02_kyc_agent.ipynb              # KYC agent running in a notebook
│   │   └── 03_kyc_agent_deploy.ipynb       # Deploy agent as a Databricks App
│   ├── scene2_txn_screening/
│   │   ├── 01_train_model_and_pipeline.ipynb  # ML model + SEPA table + pipeline
│   │   └── 02_zerobus_ingest.ipynb         # Zerobus ingest (credentials, grants, ingest)
│   └── scene6_cco_dashboard/
│       └── 01_generate_dashboard_data.py   # CCO compliance metrics generator
├── agents/
│   └── kyc_agent/                          # Databricks App source (Scene 1)
│       ├── app.yaml                        # App config and env vars
│       ├── pyproject.toml                  # App dependencies
│       ├── call_app.sh                     # CLI test script
│       └── agent_server/
│           ├── agent.py                    # Agent, tools, checkpointer, handlers
│           └── start_server.py             # Server bootstrap
├── app/                                    # Frontend app (6-scene interactive UI)
├── pipelines/
│   ├── sepa_pipeline.py                    # DLT pipeline (bronze -> silver -> gold)
│   └── requirements.txt                    # Pipeline dependencies
├── volume_assets/                          # Sample documents (passport, utility bill)
└── scripts/
    └── cleanup.sh                          # Bundle destroy helper
```

## Conversation memory

The deployed KYC agent app uses **LangGraph checkpointing** backed by **Lakebase** (Databricks managed PostgreSQL):

- **Single-message requests** (CLI, subagent): stateful via `thread_id`
- **Multi-message requests** (full history in one call): stateless
- **Fallback**: if `LAKEBASE_INSTANCE_NAME` is not set, uses in-memory checkpointing

## Troubleshooting

**`DeltaIllegalStateException: DIFFERENT_DELTA_TABLE_READ_BY_STREAMING_SOURCE`**

The pipeline checkpoint was created for one table ID, but the source table was recreated. Fix: stop the pipeline, delete the checkpoint directory, restart.

**`ZerobusException: ... tls handshake eof`**

Run `02_zerobus_ingest` on a **Databricks cluster** (not locally / not with Databricks Connect). Ensure Zerobus Ingest is enabled for your workspace.

## Cleanup

Each notebook has a "Cleanup" section at the bottom to drop its resources. For a full teardown:

```bash
databricks bundle destroy --target dev
```

Or use the helper script:

```bash
bash scripts/cleanup.sh
```

## Contributing

1. **git clone** this project locally
2. Utilize the Databricks CLI to test your changes against a Databricks workspace of your choice
3. Contribute to repositories with pull requests (PRs), ensuring that you always have a second-party review from a capable teammate

## Third-Party Package Licenses

&copy; 2025 Databricks, Inc. All rights reserved. The source in this project is provided subject to the Databricks License [[https://databricks.com/db-license-source]](https://databricks.com/db-license-source]). All included or referenced third party libraries are subject to the licenses set forth below.

| Package | License | Copyright |
|---------|---------|-----------|
| langchain | MIT | LangChain, Inc. |
| langchain-core | MIT | LangChain, Inc. |
| databricks-langchain | Apache 2.0 | Databricks, Inc. |
| databricks-sdk | Apache 2.0 | Databricks, Inc. |
| databricks-openai | Apache 2.0 | Databricks, Inc. |
| unitycatalog-ai | Apache 2.0 | Databricks, Inc. |
| mlflow | Apache 2.0 | Databricks, Inc. |
| scikit-learn | BSD-3-Clause | scikit-learn developers |
| pandas | BSD-3-Clause | pandas contributors |
| numpy | BSD-3-Clause | NumPy developers |
| pyarrow | Apache 2.0 | Apache Software Foundation |
| scipy | BSD-3-Clause | SciPy developers |
| flask | BSD-3-Clause | Pallets Projects |
| cloudpickle | BSD-3-Clause | cloudpickle contributors |
| fastapi | MIT | Sebastian Ramirez |
| uvicorn | BSD-3-Clause | Encode |
| pg8000 | BSD-3-Clause | The Contributors (PostgreSQL adapter for Lakebase connectivity) |
