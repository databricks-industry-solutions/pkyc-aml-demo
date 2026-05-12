"""
SEPA transactions medallion pipeline: bronze → silver → gold.
Pipeline parameters (set in pipeline configuration via databricks.yml):
  - catalog_name: Unity Catalog name (default main)
  - schema_name: schema name (default kyc_demo)
  - SEPA_SOURCE_TABLE: source table for bronze (default {catalog_name}.{schema_name}.sepa_transactions)
  - SEPA_FRAUD_MODEL_URI: Unity Catalog model URI for risk scoring (default models:/{catalog_name}.{schema_name}.sepa_fraud_model@Production)
Read via spark.conf.get("key", "default") per Databricks pipeline parameterization.
"""
from pyspark import pipelines as dp
from pyspark.sql import functions as F

BRONZE_TABLE = "bronze_sepa_transactions"
SILVER_TABLE = "silver_sepa_transactions"
GOLD_TABLE = "gold_sepa_transactions"
GOLD_DAILY_TABLE = "gold_sepa_daily_summary"


@dp.table(
    name=BRONZE_TABLE,
    comment="Bronze layer: Raw SEPA transactions streamed from source table",
)
def bronze_sepa_transactions():
    """
    Ingest raw SEPA transaction data from the source streaming table.
    No transformations applied - raw data ingestion only.
    """
    catalog_name = spark.conf.get("catalog_name", "main")
    schema_name = spark.conf.get("schema_name", "kyc_demo")
    default_source = f"{catalog_name}.{schema_name}.sepa_transactions"
    source_table = spark.conf.get("SEPA_SOURCE_TABLE", default_source)
    return spark.readStream.table(source_table)


@dp.table(
    name=SILVER_TABLE,
    comment="Silver layer: Cleaned and validated SEPA transactions with ML risk score",
)
def silver_sepa_transactions():
    """
    Clean and validate SEPA transactions from bronze; score each with the registered
    fraud/risk model (main.kyc_demo.sepa_fraud_model@Production). Drops null
    instruction_id and deduplicates by instruction_id. risk_level is Low/Medium/Blocked;
    if the model was logged with a numpy-inferred signature, re-log it with a pandas
    signature in the notebook so spark_udf receives correct column names.
    """
    import mlflow.pyfunc

    catalog_name = spark.conf.get("catalog_name", "main")
    schema_name = spark.conf.get("schema_name", "kyc_demo")
    default_model_uri = f"models:/{catalog_name}.{schema_name}.sepa_fraud_model@Production"
    fraud_model_uri = spark.conf.get("SEPA_FRAUD_MODEL_URI", default_model_uri)
    df = (
        spark.readStream.table(BRONZE_TABLE)
        .dropna(subset=["instruction_id"])
        .withWatermark("ingestion_time", "10 minutes")
        .dropDuplicates(["instruction_id"])
    )
    # Feature columns expected by the model (order must match training)
    df = df.withColumn("ingestion_hour", F.hour(F.col("ingestion_time")).cast("double"))
    # Use result_type="string" (IntegerType fails with model output; MLflow suggests StringType)
    score_udf = mlflow.pyfunc.spark_udf(
        spark,
        fraud_model_uri,
        result_type="string",  # model returns 0/1/2; Spark gets "0"/"1"/"2"
    )
    df = df.withColumn(
        "risk_class_str",
        score_udf(
            F.col("settlement_amount"),
            F.col("currency"),
            F.col("debtor_location"),
            F.col("creditor_location"),
            F.col("remittance_information"),
            F.col("intermediary_agent"),
            F.col("ingestion_hour"),
        ),
    )
    # Map "0"->Low, "1"->Medium, "2"->Blocked
    risk_level_expr = (
        F.when(F.col("risk_class_str") == "0", "Low")
        .when(F.col("risk_class_str") == "1", "Medium")
        .when(F.col("risk_class_str") == "2", "Blocked")
        .otherwise("Unknown")
    )
    return df.withColumn("risk_level", risk_level_expr).drop("risk_class_str")


@dp.materialized_view(
    name=GOLD_TABLE,
    comment="Gold layer: Curated SEPA transactions for downstream use",
)
def gold_sepa_transactions():
    """
    Curated pass-through from silver for analytics and ML.
    """
    return spark.table(SILVER_TABLE)


@dp.materialized_view(
    name=GOLD_DAILY_TABLE,
    comment="Gold layer: Daily summary of SEPA transactions by currency",
)
def gold_sepa_daily_summary():
    """
    Daily aggregates: count and sum of settlement_amount by date and currency.
    """
    return (
        spark.table(SILVER_TABLE)
        .withColumn("ingestion_date", F.to_date(F.col("ingestion_time")))
        .groupBy("ingestion_date", "currency")
        .agg(
            F.count("*").alias("transaction_count"),
            F.sum("settlement_amount").alias("total_settlement_amount"),
        )
    )
