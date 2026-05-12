# Databricks notebook source
# MAGIC %md
# MAGIC # CCO Dashboard - Sample Data Generator
# MAGIC
# MAGIC Generates a single denormalized table with all compliance metrics for easy dashboarding.

# COMMAND ----------

# COMMAND ----------

# MAGIC %run ../_shared/config

# COMMAND ----------

# CATALOG and SCHEMA come from %run ../_shared/config
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"USE {CATALOG}.{SCHEMA}")

# COMMAND ----------

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate One Big Table: `compliance_metrics`

# COMMAND ----------

def generate_compliance_data(n_records=20000):
    """Generate a single denormalized table with all compliance event data"""
    
    regions = ['EMEA', 'APAC', 'Americas']
    products = ['Retail Banking', 'Corporate Banking', 'Trade Finance', 'Wealth Management', 'Payments']
    
    records = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(n_records):
        event_date = base_date + timedelta(days=random.randint(0, 364))
        region = random.choice(regions)
        product = random.choice(products)
        
        # Event type determines what fields are populated
        event_type = random.choices(
            ['Alert', 'SAR Filing', 'KYC Onboarding', 'Screening Hit', 'Periodic Review', 'Blocked Transaction'],
            weights=[0.45, 0.03, 0.25, 0.15, 0.10, 0.02]
        )[0]
        
        record = {
            'record_id': f'REC-{i+1:06d}',
            'event_date': event_date,
            'event_month': event_date.strftime('%Y-%m'),
            'event_week': event_date.strftime('%Y-W%W'),
            'region': region,
            'product': product,
            'event_type': event_type,
            'customer_id': f'CUST-{random.randint(10000, 59999)}',
            'analyst_id': f'analyst_{random.randint(1, 30):02d}',
            
            # Alert fields
            'alert_type': None,
            'alert_status': None,
            'alert_outcome': None,
            'alert_risk_score': None,
            'alert_handling_hours': None,
            'alert_sla_hours': None,
            'alert_within_sla': None,
            'alert_overdue': None,
            'alert_auto_resolved': None,
            'is_false_positive': None,
            
            # SAR fields
            'sar_days_to_file': None,
            'sar_within_deadline': None,
            'sar_amount': None,
            
            # KYC fields
            'customer_type': None,
            'customer_risk_rating': None,
            'kyc_complete': None,
            'beneficial_ownership_complete': None,
            'onboarding_time_minutes': None,
            
            # Screening fields
            'screening_type': None,
            'screening_status': None,
            'screening_clearance_hours': None,
            'screening_within_sla': None,
            
            # Periodic review fields
            'review_risk_tier': None,
            'review_on_time': None,
            'risk_rating_changed': None,
            'risk_upgrade': None,
            'risk_downgrade': None,
            
            # Blocked transaction fields
            'blocked_amount': None,
            'block_reason': None,
        }
        
        # Populate based on event type
        if event_type == 'Alert':
            record['alert_type'] = random.choice(['Transaction Monitoring', 'Sanctions', 'PEP', 'Adverse Media', 'Behavior Pattern'])
            record['alert_status'] = random.choices(
                ['Closed - No SAR', 'Closed - SAR Filed', 'Open', 'In Progress'],
                weights=[0.55, 0.05, 0.15, 0.25]
            )[0]
            record['alert_risk_score'] = round(random.uniform(0.3, 0.99), 2)
            record['alert_sla_hours'] = 24
            
            if 'Closed' in record['alert_status']:
                record['alert_handling_hours'] = round(max(0.5, np.random.exponential(6)), 2)
                record['alert_within_sla'] = record['alert_handling_hours'] <= 24
                record['alert_overdue'] = not record['alert_within_sla']
                record['alert_auto_resolved'] = random.random() < 0.34
                
                if record['alert_status'] == 'Closed - SAR Filed':
                    record['alert_outcome'] = 'True Positive'
                    record['is_false_positive'] = False
                else:
                    record['alert_outcome'] = random.choices(['False Positive', 'True Positive'], weights=[0.67, 0.33])[0]
                    record['is_false_positive'] = record['alert_outcome'] == 'False Positive'
            else:
                # Check if overdue (open > 24 hours)
                record['alert_overdue'] = random.random() < 0.004  # 0.4% overdue
        
        elif event_type == 'SAR Filing':
            record['sar_days_to_file'] = random.randint(1, 35)
            record['sar_within_deadline'] = record['sar_days_to_file'] <= 30
            record['sar_amount'] = round(random.uniform(10000, 2000000), 2)
        
        elif event_type == 'KYC Onboarding':
            record['customer_type'] = random.choices(['Individual', 'Legal Entity'], weights=[0.7, 0.3])[0]
            record['customer_risk_rating'] = random.choices(
                ['Low', 'Medium', 'High', 'Very High'],
                weights=[0.72, 0.21, 0.05, 0.02]
            )[0]
            record['kyc_complete'] = random.random() < 0.987
            record['beneficial_ownership_complete'] = random.random() < 0.963 if record['customer_type'] == 'Legal Entity' else None
            record['onboarding_time_minutes'] = round(max(1, np.random.exponential(4.7)), 1)
        
        elif event_type == 'Screening Hit':
            record['screening_type'] = random.choices(
                ['OFAC', 'EU Sanctions', 'UN Sanctions', 'PEP', 'Adverse Media'],
                weights=[0.15, 0.20, 0.10, 0.35, 0.20]
            )[0]
            record['screening_status'] = random.choices(
                ['Cleared - False Positive', 'Cleared - True Match', 'Pending'],
                weights=[0.85, 0.05, 0.10]
            )[0]
            if 'Cleared' in record['screening_status']:
                record['screening_clearance_hours'] = round(max(0.5, np.random.exponential(2)), 2)
                record['screening_within_sla'] = record['screening_clearance_hours'] <= 4
        
        elif event_type == 'Periodic Review':
            record['review_risk_tier'] = random.choices(
                ['Low', 'Medium', 'High', 'Very High'],
                weights=[0.72, 0.21, 0.05, 0.02]
            )[0]
            record['review_on_time'] = random.random() < 0.914
            record['risk_rating_changed'] = random.random() < 0.15
            if record['risk_rating_changed']:
                record['risk_upgrade'] = random.random() < 0.37
                record['risk_downgrade'] = not record['risk_upgrade']
        
        elif event_type == 'Blocked Transaction':
            record['blocked_amount'] = round(random.uniform(5000, 500000), 2)
            record['block_reason'] = random.choice(['Sanctions Match', 'KYC Incomplete', 'Suspicious Activity', 'PEP Concern', 'High Risk Country'])
        
        records.append(record)
    
    return pd.DataFrame(records)

# Generate the data
df = generate_compliance_data(20000)
spark_df = spark.createDataFrame(df)
spark_df.write.mode("overwrite").saveAsTable("compliance_metrics")

print(f"✅ Created compliance_metrics table with {df.shape[0]} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Also create a summary/KPI table for quick reference

# COMMAND ----------

# Create a pre-aggregated KPI summary table
kpi_data = [
    # Alert metrics
    {'kpi_category': 'Alerts', 'kpi_name': 'Total Alert Volume (30d)', 'kpi_value': 2847.0, 'kpi_target': None, 'trend': -12.0, 'trend_direction': 'down'},
    {'kpi_category': 'Alerts', 'kpi_name': 'Open Alert Backlog', 'kpi_value': 487.0, 'kpi_target': 500.0, 'trend': -23.0, 'trend_direction': 'down'},
    {'kpi_category': 'Alerts', 'kpi_name': 'False Positive Rate %', 'kpi_value': 67.0, 'kpi_target': 70.0, 'trend': -15.0, 'trend_direction': 'down'},
    {'kpi_category': 'Alerts', 'kpi_name': 'Avg Handling Time (hours)', 'kpi_value': 4.2, 'kpi_target': 8.0, 'trend': -8.0, 'trend_direction': 'down'},
    {'kpi_category': 'Alerts', 'kpi_name': '95th Percentile Handling Time (hours)', 'kpi_value': 18.0, 'kpi_target': 24.0, 'trend': -5.0, 'trend_direction': 'down'},
    {'kpi_category': 'Alerts', 'kpi_name': 'SLA Compliance %', 'kpi_value': 94.2, 'kpi_target': 90.0, 'trend': 2.0, 'trend_direction': 'up'},
    {'kpi_category': 'Alerts', 'kpi_name': 'Overdue Alerts', 'kpi_value': 12.0, 'kpi_target': 0.0, 'trend': -3.0, 'trend_direction': 'down'},
    {'kpi_category': 'Alerts', 'kpi_name': 'Auto-Resolved Rate %', 'kpi_value': 34.2, 'kpi_target': 30.0, 'trend': 18.0, 'trend_direction': 'up'},
    
    # SAR metrics
    {'kpi_category': 'SAR Filing', 'kpi_name': 'SAR Filings (30d)', 'kpi_value': 142.0, 'kpi_target': None, 'trend': 8.0, 'trend_direction': 'up'},
    {'kpi_category': 'SAR Filing', 'kpi_name': 'SAR Conversion Rate %', 'kpi_value': 4.99, 'kpi_target': 5.0, 'trend': 0.5, 'trend_direction': 'up'},
    {'kpi_category': 'SAR Filing', 'kpi_name': 'Avg Days to File SAR', 'kpi_value': 3.2, 'kpi_target': 30.0, 'trend': -0.5, 'trend_direction': 'down'},
    {'kpi_category': 'SAR Filing', 'kpi_name': 'Within Regulatory Deadline %', 'kpi_value': 98.6, 'kpi_target': 100.0, 'trend': 1.0, 'trend_direction': 'up'},
    
    # KYC metrics
    {'kpi_category': 'KYC', 'kpi_name': 'KYC Completion Rate %', 'kpi_value': 98.7, 'kpi_target': 98.0, 'trend': 0.5, 'trend_direction': 'up'},
    {'kpi_category': 'KYC', 'kpi_name': 'Beneficial Ownership Coverage %', 'kpi_value': 96.3, 'kpi_target': 95.0, 'trend': 2.1, 'trend_direction': 'up'},
    {'kpi_category': 'KYC', 'kpi_name': 'Avg Onboarding Time (min)', 'kpi_value': 4.7, 'kpi_target': 10.0, 'trend': -62.0, 'trend_direction': 'down'},
    {'kpi_category': 'KYC', 'kpi_name': 'High-Risk Reviews On Time %', 'kpi_value': 91.4, 'kpi_target': 90.0, 'trend': 1.2, 'trend_direction': 'up'},
    
    # Risk distribution
    {'kpi_category': 'Risk', 'kpi_name': 'Low Risk Customers %', 'kpi_value': 72.4, 'kpi_target': None, 'trend': 0.3, 'trend_direction': 'up'},
    {'kpi_category': 'Risk', 'kpi_name': 'Medium Risk Customers %', 'kpi_value': 21.3, 'kpi_target': None, 'trend': -0.2, 'trend_direction': 'down'},
    {'kpi_category': 'Risk', 'kpi_name': 'High Risk Customers %', 'kpi_value': 5.1, 'kpi_target': None, 'trend': -0.1, 'trend_direction': 'down'},
    {'kpi_category': 'Risk', 'kpi_name': 'Very High Risk Customers %', 'kpi_value': 1.2, 'kpi_target': None, 'trend': 0.0, 'trend_direction': 'flat'},
    {'kpi_category': 'Risk', 'kpi_name': 'Risk Score Changes (period)', 'kpi_value': 234.0, 'kpi_target': None, 'trend': 12.0, 'trend_direction': 'up'},
    
    # Screening metrics
    {'kpi_category': 'Screening', 'kpi_name': 'OFAC/Sanctions Hit Rate %', 'kpi_value': 0.12, 'kpi_target': None, 'trend': 0.0, 'trend_direction': 'flat'},
    {'kpi_category': 'Screening', 'kpi_name': 'PEP Hit Rate %', 'kpi_value': 0.34, 'kpi_target': None, 'trend': 0.02, 'trend_direction': 'up'},
    {'kpi_category': 'Screening', 'kpi_name': 'Avg Clearance Time (hours)', 'kpi_value': 2.1, 'kpi_target': 4.0, 'trend': -0.3, 'trend_direction': 'down'},
    {'kpi_category': 'Screening', 'kpi_name': 'Clearance SLA Compliance %', 'kpi_value': 97.8, 'kpi_target': 95.0, 'trend': 1.5, 'trend_direction': 'up'},
    
    # Operations
    {'kpi_category': 'Operations', 'kpi_name': 'Blocked Transactions', 'kpi_value': 23.0, 'kpi_target': None, 'trend': -5.0, 'trend_direction': 'down'},
    {'kpi_category': 'Operations', 'kpi_name': 'Blocked Amount (EUR M)', 'kpi_value': 4.2, 'kpi_target': None, 'trend': None, 'trend_direction': None},
    {'kpi_category': 'Operations', 'kpi_name': 'Cases per Day (Team)', 'kpi_value': 847.0, 'kpi_target': 800.0, 'trend': 5.0, 'trend_direction': 'up'},
    {'kpi_category': 'Operations', 'kpi_name': 'Cases per FTE', 'kpi_value': 28.0, 'kpi_target': 25.0, 'trend': 2.0, 'trend_direction': 'up'},
    
    # Compliance & Audit
    {'kpi_category': 'Audit', 'kpi_name': 'Open Audit Findings', 'kpi_value': 7.0, 'kpi_target': 0.0, 'trend': -2.0, 'trend_direction': 'down'},
    {'kpi_category': 'Audit', 'kpi_name': 'YTD Fines (EUR)', 'kpi_value': 0.0, 'kpi_target': 0.0, 'trend': 0.0, 'trend_direction': 'flat'},
    {'kpi_category': 'Audit', 'kpi_name': 'Training Completion %', 'kpi_value': 97.3, 'kpi_target': 95.0, 'trend': 1.2, 'trend_direction': 'up'},
    {'kpi_category': 'Audit', 'kpi_name': 'Avg Training Score', 'kpi_value': 92.0, 'kpi_target': 80.0, 'trend': 2.0, 'trend_direction': 'up'},
    {'kpi_category': 'Audit', 'kpi_name': 'Controls Effectiveness %', 'kpi_value': 94.1, 'kpi_target': 90.0, 'trend': 1.5, 'trend_direction': 'up'},
]

kpi_df = spark.createDataFrame(kpi_data)
kpi_df.write.mode("overwrite").saveAsTable("kpi_summary")
print(f"✅ Created kpi_summary table with {len(kpi_data)} KPIs")

# COMMAND ----------



# COMMAND ----------

# DBTITLE 1,Executive KPI Summary


# COMMAND ----------

# MAGIC %md
# MAGIC ## View the Tables

# COMMAND ----------

display(spark.table("compliance_metrics").limit(10))

# COMMAND ----------

display(spark.table("kpi_summary"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Dashboard Queries

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Alert volume by region and month
# MAGIC SELECT 
# MAGIC   event_month,
# MAGIC   region,
# MAGIC   COUNT(*) as alert_count
# MAGIC FROM compliance_metrics
# MAGIC WHERE event_type = 'Alert'
# MAGIC GROUP BY event_month, region
# MAGIC ORDER BY event_month, region

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Customer risk distribution
# MAGIC SELECT 
# MAGIC   customer_risk_rating,
# MAGIC   COUNT(*) as count,
# MAGIC   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as pct
# MAGIC FROM compliance_metrics
# MAGIC WHERE event_type = 'KYC Onboarding' AND customer_risk_rating IS NOT NULL
# MAGIC GROUP BY customer_risk_rating

# COMMAND ----------

# MAGIC %sql
# MAGIC -- All KPIs from summary table
# MAGIC SELECT * FROM kpi_summary ORDER BY kpi_category, kpi_name

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC 1. Go to **SQL Editor → Dashboards → Create**
# MAGIC 2. Use `kpi_summary` table for quick KPI cards
# MAGIC 3. Use `compliance_metrics` table for detailed charts
# MAGIC 4. Create Genie Space with both tables
# MAGIC 5. Embed in the app

# COMMAND ----------

print("""
✅ Done! Two tables created:

1. compliance_metrics - 20,000 rows of detailed event data
   Use for: Charts, trends, drill-downs

2. kpi_summary - 35 pre-calculated KPIs  
   Use for: KPI cards, scorecards

Both tables are in: {}.{}
""".format(CATALOG, SCHEMA))
