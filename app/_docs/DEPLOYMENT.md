# Deploying to Databricks Apps

This guide walks you through deploying the Transaction Screening demo to Databricks Apps.

## Prerequisites

- Databricks workspace (AWS, Azure, or GCP)
- Workspace admin or user with Apps permissions
- Git repository (recommended) or local files

## Deployment Steps

### Option 1: Deploy from Git Repository (Recommended)

1. **Push your code to a Git repository** (GitHub, GitLab, Bitbucket, etc.)
   ```bash
   git add .
   git commit -m "Prepare for Databricks Apps deployment"
   git push origin main
   ```

2. **In Databricks Workspace:**
   - Navigate to **Apps** in the left sidebar
   - Click **Create App**
   - Choose **"From Git"**
   - Enter your repository URL
   - Select branch: `main` (or your branch)
   - Databricks will auto-detect `app.yaml`

3. **Configure Environment Variables** (in the Apps UI):
   - `DATABRICKS_WORKSPACE_URL`: Your workspace URL (e.g., `https://dbc-abc123.cloud.databricks.com`)
   - `UNITY_CATALOG_NAME`: Your catalog name (e.g., `financial_crime`)
   - `SCHEMA_NAME`: Your schema name (e.g., `kyc_monitoring`)

4. **Deploy:**
   - Click **Deploy**
   - Wait for deployment (2-3 minutes)
   - You'll get a public URL like: `https://your-workspace.apps.databricks.com/your-app-name`

### Option 2: Deploy from Workspace Files

1. **Upload files to Databricks Workspace:**
   - Go to **Workspace** in Databricks
   - Create a folder (e.g., `/Users/your.name/txn-screening-demo`)
   - Upload all HTML, JS, config, and Python files

2. **Create App:**
   - Navigate to **Apps** in the left sidebar
   - Click **Create App**
   - Choose **"From Workspace"**
   - Select your folder
   - Databricks will detect `app.yaml`

3. **Configure & Deploy** (same as Option 1, steps 3-4)

## Updating Your Deployment

### Automatic Updates (Git-based deployment)
If deployed from Git, push updates to trigger redeployment:
```bash
git add .
git commit -m "Update demo"
git push origin main
```

Then in Databricks Apps UI:
- Go to your App
- Click **Update** or **Redeploy**

### Manual Updates (Workspace-based deployment)
- Upload updated files to your workspace folder
- Click **Redeploy** in the Apps UI

## Adding Links to Real Databricks Assets

Once you've deployed your real pipelines, tables, and dashboards, you can update the demo to link to them.

### Step 1: Update Environment Variables in `app.yaml`

Edit the asset links in your deployment:

```yaml
env:
  - name: DATABRICKS_WORKSPACE_URL
    value: "https://your-workspace.cloud.databricks.com"
  
  - name: UNITY_CATALOG_NAME
    value: "financial_crime"
  
  - name: SCHEMA_NAME
    value: "kyc_monitoring"
  
  # Add your real pipeline/dashboard IDs
  - name: DLT_PIPELINE_ID
    value: "abc123-pipeline-id"
  
  - name: DASHBOARD_ID
    value: "def456-dashboard-id"
```

### Step 2: Inject Links into HTML (Future Enhancement)

When you want to add clickable links, modify your HTML scenes to call the `/api/assets` endpoint:

**Example JavaScript snippet to add to any scene:**

```javascript
// Fetch asset links from backend
async function loadAssetLinks() {
    const response = await fetch('/api/assets');
    const assets = await response.json();
    
    // Example: Add link to Unity Catalog table
    const tableLink = document.getElementById('customer-table-link');
    if (tableLink) {
        tableLink.href = assets.customer_table;
        tableLink.target = '_blank';
    }
    
    // Example: Add link to DLT pipeline
    const pipelineLink = document.getElementById('dlt-pipeline-link');
    if (pipelineLink) {
        pipelineLink.href = assets.dlt_pipeline;
        pipelineLink.target = '_blank';
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', loadAssetLinks);
```

**Example HTML additions:**

```html
<!-- In Scene 2: Transaction Screening -->
<div class="asset-link-card">
    <h4>🔗 View Real Pipeline</h4>
    <a id="dlt-pipeline-link" href="#" class="text-blue-400 hover:text-blue-300">
        Open DLT Pipeline in Workspace →
    </a>
</div>

<!-- In Scene 3: AI Monitoring -->
<div class="asset-link-card">
    <h4>🔗 View Customer Table</h4>
    <a id="customer-table-link" href="#" class="text-blue-400 hover:text-blue-300">
        Open Unity Catalog Table →
    </a>
</div>
```

### Step 3: Update `app.py` with Real Asset IDs

Edit the `ASSET_LINKS` dictionary in `app.py`:

```python
ASSET_LINKS = {
    'customer_table': f'{WORKSPACE_URL}/explore/data/{CATALOG_NAME}/{SCHEMA_NAME}/customers',
    'transaction_table': f'{WORKSPACE_URL}/explore/data/{CATALOG_NAME}/{SCHEMA_NAME}/transactions',
    'dlt_pipeline': f'{WORKSPACE_URL}/pipelines/{os.getenv("DLT_PIPELINE_ID", "YOUR_PIPELINE_ID")}',
    'ml_model': f'{WORKSPACE_URL}/ml/models/transaction_risk_model',
    'dashboard': f'{WORKSPACE_URL}/sql/dashboards/{os.getenv("DASHBOARD_ID", "YOUR_DASHBOARD_ID")}',
    'workflow': f'{WORKSPACE_URL}/jobs/YOUR_JOB_ID',
}
```

## Testing Locally Before Deployment

You can test the Flask app locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABRICKS_WORKSPACE_URL="https://your-workspace.cloud.databricks.com"
export UNITY_CATALOG_NAME="financial_crime"
export SCHEMA_NAME="kyc_monitoring"

# Run Flask app
python app.py

# Open browser to http://localhost:8080
```

## Sharing Your Demo

Once deployed to Databricks Apps, you'll get a public URL that you can share:

```
https://your-workspace.apps.databricks.com/txn-screening-demo
```

**Sharing Options:**
1. **Public Demo** - Anyone with the link can access (if permissions allow)
2. **Internal Only** - Restrict to users in your Databricks workspace
3. **Catalog Integration** - Publish to Databricks Demo Catalog for broader discovery

Configure access in the Apps settings UI.

## Architecture After Deployment

```
┌─────────────────────────────────────────────────┐
│         Databricks Apps (Flask Server)          │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │   HTML Demo (Presentation Layer)        │    │
│  │   - 5 Scenes (Onboarding → SAR)        │    │
│  │   - Interactive Visualizations          │    │
│  │   - Clickable Links ↓                   │    │
│  └────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────┘
                       │ Links to real assets
                       ↓
┌─────────────────────────────────────────────────┐
│      Real Databricks Assets (Separate)          │
│                                                  │
│  • Unity Catalog Tables (customers, txns)       │
│  • DLT Pipelines (streaming ingestion)          │
│  • ML Models (risk scoring)                     │
│  • SQL Dashboards (monitoring)                  │
│  • Workflows (investigation automation)         │
└─────────────────────────────────────────────────┘
```

## Troubleshooting

### App won't start
- Check `app.yaml` syntax
- Verify `requirements.txt` has correct packages
- Check app logs in Databricks Apps UI

### Links not working
- Verify environment variables are set correctly
- Check workspace URL format (no trailing slash)
- Ensure asset IDs are correct

### Static files not loading
- Verify all HTML/JS/CSS files are in the same directory as `app.py`
- Check Flask static file routing

## Next Steps

1. ✅ Deploy the demo to Databricks Apps (showcase/presentation layer)
2. 🔨 Build your real features separately:
   - Create Unity Catalog schema and tables
   - Build DLT pipeline for transaction ingestion
   - Train and register ML models
   - Create SQL dashboards
3. 🔗 Add clickable links from demo HTML to real assets
4. 📊 Publish to Databricks Demo Catalog for org-wide sharing

## Support

For issues with:
- **Databricks Apps deployment**: Contact Databricks support or check [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- **Demo customization**: See main `README.md`

