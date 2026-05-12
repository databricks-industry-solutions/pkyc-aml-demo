# Volume assets (bundled files)

Files in this folder are **synced with the bundle** when you run `databricks bundle deploy`. They appear in your workspace under the same path.

**For the KYC demo**, add sample files here so they can be copied to the agent volume:

- `passport_dirk_van_dijk.png` – sample passport image for the demo
- `utility_bill_dirk_van_dijk.png` – sample proof-of-address image

**Naming convention:** Files follow the pattern `passport_<first_name>_<last_name>.png` and `utility_bill_<first_name>_<last_name>.png` (lowercase, spaces replaced with underscores). The agent tools resolve the file path automatically from the user's name.

After deployment, run the **"Copy bundled files to volume"** cell in `00_kyc_setup.ipynb` once to copy these files into the agent volume (`agent_volume`). The agent then looks up paths like `{VOLUME_PATH}/passport_dirk_van_dijk.png` based on the user's name.

You can also upload files directly to the volume in the Databricks UI (Data → Volumes → your catalog/schema → agent_volume).
