# Databricks notebook source
# MAGIC %md
# MAGIC ## Demo Constants
# MAGIC Shared SEPA transaction constants (companies, locations, intermediaries, remittance types, currencies) used by the ML training notebook and the Zerobus ingest notebook.

# COMMAND ----------

COMPANIES = [
    "Acme Corp", "Beta Ltd", "Gamma Industries", "Delta Finance", "Epsilon Trading",
    "Zeta Holdings", "Sigma Solutions", "Omega Bank", "Atlas Logistics", "Nova Tech",
    "Offshore Holdings Ltd", "Global Transfer Corp", "Euro Commerce AG", "Nordic Investments Ltd",
    "Mediterranean Trading Co", "Alpine Finance AG", "Continental Payments Ltd", "Pacific Rim Corp",
]

DEBTOR_LOCATIONS = [
    "Dublin", "Paris", "Amsterdam", "Berlin", "Madrid", "Rome", "Brussels", "Vienna",
    "Luxembourg", "Nicosia", "Gibraltar", "Panama City", "George Town", "Moscow", "Minsk", "Caracas", "Lagos",
]

CREDITOR_LOCATIONS = [
    "Frankfurt", "London", "Amsterdam", "Madrid", "Milan", "Barcelona", "Luxembourg", "Zurich",
    "Nicosia", "Gibraltar", "Panama City", "George Town", "Moscow", "Caracas", "Lagos",
]

INTERMEDIARY_AGENTS = [
    "Deutsche Bank AG", "BNP Paribas", "ING Bank", "Commerzbank AG",
    "Santander", "UniCredit", "Rabobank", "KBC Bank",
    "Offshore Trust Bank Ltd", "Global Transfer Services AG", "Euro Clearing House",
    "Pan-European Payments AG", "Atlantic Finance Ltd", "Pacific Rim Bank Corp",
]

REMITTANCE_TYPES = [
    "Invoice payment", "Salary", "Supplier payment", "Dividend", "Loan repayment",
    "Rent", "Subscription", "Refund", "Royalty", "Consulting fee",
    "Cash transfer", "Investment", "Commission", "Cryptocurrency sale", "Intercompany loan",
    "Settlement payment", "Fee payment", "Insurance premium", "License fee",
]

CURRENCIES = ["EUR", "GBP", "CHF"]
