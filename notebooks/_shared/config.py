# Databricks notebook source
# MAGIC %md
# MAGIC ## Demo Configuration
# MAGIC Edit the values below, then run any notebook — they all pick this up via `%run`.

# COMMAND ----------

# ── Edit your settings here ────────────────────────────────────────────
CATALOG         = "main"
SCHEMA          = "kyc_demo"
SEPA_TABLE_NAME = "sepa_transactions"
PIPELINE_NAME   = "SEPA KYC Demo Pipeline"
# ───────────────────────────────────────────────────────────────────────

# Override from job parameters when run as a workflow task.
for _var in ["catalog", "schema", "sepa_table_name", "pipeline_name"]:
    try:
        _val = dbutils.widgets.get(_var)
        if _val.strip():
            globals()[_var.upper()] = _val.strip()
    except Exception:
        pass

# Derived
CATALOG_SCHEMA  = f"{CATALOG}.{SCHEMA}"
VOLUME_PATH     = f"/Volumes/{CATALOG}/{SCHEMA}/agent_volume"
SEPA_TABLE_FULL = f"{CATALOG}.{SCHEMA}.{SEPA_TABLE_NAME}"

print(f"Config: CATALOG={CATALOG}, SCHEMA={SCHEMA}, SEPA_TABLE={SEPA_TABLE_NAME}")
