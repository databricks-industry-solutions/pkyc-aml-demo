Copyright (2025) Databricks, Inc.

This Software includes software developed at Databricks (https://www.databricks.com/) and its use is subject to the included LICENSE file.
By using this repository and the notebooks within, you consent to Databricks collection and use of usage and tracking information in accordance with our privacy policy at www.databricks.com/privacypolicy.

---

## Synthetic Data Notice

All data used in this repository is **entirely fictitious** and generated programmatically. No real customer, personal, or financial data is used at any point.

### Document images (passport and utility bill)

Passport and utility bill images are synthetic document images generated at runtime with **Python Pillow** (BSD-3-Clause) and uploaded directly to the Unity Catalog volume. The default demo persona "Dirk van Dijk" is entirely fictitious — the name, date of birth, address, passport number, and all other fields are made-up placeholders with no relation to any real person.

To generate images for any persona, run:

```
notebooks/scene1_kyc_onboarding/01_kyc_data_setup.ipynb
```

No external AI service or third-party image-generation tool is required. The notebook creates the Unity Catalog schema and volume (if they do not yet exist) before generating and uploading the images.

### SEPA transaction data

Synthetic SEPA payment transactions (sender/receiver names, IBANs, amounts, currencies) are generated programmatically in:

```
notebooks/scene2_txn_screening/01_train_model_and_pipeline.ipynb
```

Company names, IBAN prefixes, cities, and currencies are drawn from a fixed vocabulary defined in `notebooks/_shared/sepa_constants.py`. All values are fictitious.

### Screening seed tables (PEP, sanctions, fraud, SBI risk)

Demo PEP, sanctions, fraud blacklist, and SBI risk-code tables are created with hardcoded fictitious entries in:

```
notebooks/scene1_kyc_onboarding/01_kyc_data_setup.ipynb
```

No real names, organisations, or sanctions data are used. The tables exist solely to demonstrate the screening workflow.

### CCO dashboard metrics

Compliance KPI and metrics tables are synthetically generated in:

```
notebooks/scene6_cco_dashboard/01_generate_dashboard_data.py
```

All figures are random/illustrative and do not represent real compliance outcomes.
