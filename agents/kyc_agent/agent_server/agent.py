"""
KYC Onboarding Agent - Databricks App (Responses API).

Exposes the BankBricks KYC onboarding agent via /invocations so it can be
used as a subagent by the multi-agent orchestrator (apps/<app-name>).

Uses the Databricks SQL Statement Execution API (via databricks-sdk) for
document parsing and account creation — no Spark session required.
"""

import json
import logging
import os
import re
import time
import uuid
from typing import Any

import mlflow
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementParameterListItem, StatementState
from mlflow.genai.agent_server import invoke, stream
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CATALOG_SCHEMA = os.getenv("CATALOG_SCHEMA", "main.kyc_demo")
VOLUME_PATH = os.getenv("VOLUME_PATH", "/Volumes/main/kyc_demo/agent_volume")
DEMO_SBI_CODE = os.getenv("DEMO_SBI_CODE", "47.11")
WAREHOUSE_ID = os.environ["WAREHOUSE_ID"]
ACCOUNTS_TABLE = f"{CATALOG_SCHEMA}.accounts"
LAKEBASE_INSTANCE_NAME = os.getenv("LAKEBASE_INSTANCE_NAME")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SQL execution helper (Statement Execution API — no Spark needed)
# ---------------------------------------------------------------------------
_ws_client = None


def _get_ws_client() -> WorkspaceClient:
    global _ws_client
    if _ws_client is None:
        _ws_client = WorkspaceClient()
    return _ws_client


def _execute_sql(sql: str) -> list[dict]:
    """Execute SQL via the Statement Execution API and return rows as dicts."""
    w = _get_ws_client()
    resp = w.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=sql,
        wait_timeout="0s",
    )
    # Poll until complete (AI functions like ai_parse_document can take 30-90s)
    while resp.status.state in (StatementState.PENDING, StatementState.RUNNING):
        time.sleep(2)
        resp = w.statement_execution.get_statement(resp.statement_id)

    if resp.status.state != StatementState.SUCCEEDED:
        error = getattr(resp.status, "error", None)
        raise RuntimeError(f"SQL failed ({resp.status.state}): {error}")

    # Non-SELECT statements (CREATE TABLE, INSERT) may not return columns/rows
    if not resp.manifest or not resp.manifest.schema or not resp.manifest.schema.columns:
        return []

    columns = [col.name for col in resp.manifest.schema.columns]
    rows = []
    for row_data in (resp.result.data_array or []):
        rows.append(dict(zip(columns, row_data)))
    return rows


# ---------------------------------------------------------------------------
# SQL builders (ported from 01_kyc_agent.ipynb)
# ---------------------------------------------------------------------------
def _parse_passport_sql(file_path: str) -> str:
    """Build SQL to parse a passport via READ_FILES + ai_parse_document + ai_extract."""
    if not re.match(r"^(/Volumes/|s3://|abfss://|gs://)[\w\-\./]+$", file_path):
        return "Error: path must start with /Volumes/, s3://, abfss://, or gs://"
    safe = file_path.replace("'", "''")
    return f"""
WITH file_data AS (
  SELECT path, content FROM READ_FILES('{safe}', format => 'binaryFile') LIMIT 1
),
parsed_docs AS (
  SELECT path, ai_parse_document(content, map('version', '2.0')) AS parsed FROM file_data
),
parsed_text AS (
  SELECT path, try_cast(parsed:error_status AS STRING) AS parse_error,
    concat_ws('\\n\\n', transform(try_cast(parsed:document:elements AS ARRAY<VARIANT>), element -> try_cast(element:content AS STRING))) AS text
  FROM parsed_docs
),
extracted AS (
  SELECT path, parse_error,
    ai_extract(text, array('first_name', 'last_name', 'country', 'date_of_birth', 'passport_issue_date', 'passport_expiry_date')) AS kyc
  FROM parsed_text
)
SELECT try_cast(kyc.first_name AS STRING) AS first_name, try_cast(kyc.last_name AS STRING) AS last_name,
  try_cast(kyc.country AS STRING) AS country, try_cast(kyc.date_of_birth AS STRING) AS date_of_birth,
  try_cast(kyc.passport_issue_date AS STRING) AS passport_issue_date, try_cast(kyc.passport_expiry_date AS STRING) AS passport_expiry_date,
  parse_error AS error FROM extracted
"""


def _parse_document_sql(file_path: str, extract_fields: list[str]) -> str:
    """Build SQL for any document via READ_FILES + ai_parse_document + ai_extract."""
    if not re.match(r"^(/Volumes/|s3://|abfss://|gs://)[\w\-\./]+$", file_path):
        return "Error: path must start with /Volumes/, s3://, abfss://, or gs://"
    safe = file_path.replace("'", "''")
    fields_str = ", ".join(f"try_cast(doc.{f} AS STRING) AS {f}" for f in extract_fields)
    arr = "array(" + ", ".join(f"'{f}'" for f in extract_fields) + ")"
    return f"""
WITH file_data AS (
  SELECT path, content FROM READ_FILES('{safe}', format => 'binaryFile') LIMIT 1
),
parsed_docs AS (
  SELECT path, ai_parse_document(content, map('version', '2.0')) AS parsed FROM file_data
),
parsed_text AS (
  SELECT path, try_cast(parsed:error_status AS STRING) AS parse_error,
    concat_ws('\\n\\n', transform(try_cast(parsed:document:elements AS ARRAY<VARIANT>), element -> try_cast(element:content AS STRING))) AS text
  FROM parsed_docs
),
extracted AS (
  SELECT path, parse_error, ai_extract(text, {arr}) AS doc FROM parsed_text
)
SELECT {fields_str}, parse_error AS error FROM extracted
"""


# ---------------------------------------------------------------------------
# System prompt (full conversation flow from notebook 01)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a friendly onboarding assistant for BankBricks. Follow this conversation flow exactly. Be warm and concise.

## Conversation flow

1. **Opening (if no name yet)**
   Say: "Hello! Welcome to BankBricks. To get started, what is your full name?"

2. **After user gives full name**
   Extract their first name and say: "Great! Can I call you {first_name}?" (use their actual first name.)

3. **After they confirm (e.g. yes / sure)**
   Say: "Perfect, {first_name}! What type of account would you like to open today? You can choose one or more: **Personal Current Account**, **SME Business Account**, **Investment Account**."

4. **After they pick account type(s)**
   Say: "Excellent choice! I'll set those up for you."
   **Account-specific paths (run only for the chosen types):**
   - **SME Business Account:** Call **check_customer_risk('<DEMO_SBI_CODE>')** (assumed SBI). Do not show the raw result; keep for final outcome after Proof of Address. **If the result has risk_level 'high', do NOT create the SME Business Account later**—instead inform the user we cannot open it due to risk.
   - **Investment Account:** Walk-through path that just passes (no extra tool; proceed).
   - **Personal Current Account:** Blank pass (no check; proceed).
   Do not run check_customer_risk for Personal Current or Investment only.

5. **Identity step**
   Say: "First, let's verify your identity. Please scan your passport using your camera. (For the demo, I'll look up your passport automatically.)"
   **STOP here. Wait for user to reply before continuing.**

6. **Passport verification (when the user says they scanned their passport)**
   - Call **extract_kyc('dirk', 'van_dijk')** — the demo volume always contains Dirk van Dijk's documents regardless of the user's name.
   - Also call **check_pep**, **check_sanctions**, **check_sanctioned_country**, and **check_fraud** with the first_name, last_name (and country, date_of_birth for pep/sanctions; country for sanctioned-country check) from the extract_kyc result. Do not tell the user you are running these; do not show the raw results. Keep PEP/sanctions/sanctioned-country/fraud outcome for later.
   - When extract_kyc returns successfully, reply: "Great! Verifying your document now...\n\nIdentity Verified! Your passport has been validated.\n\nPerfect! One more step - please upload a Proof of Address document. (Recent Utility Bill or Bank Statement)"
   - **STOP here. Do NOT call extract_proof_of_address yet. Do NOT create accounts yet. Wait for the user to upload their document.**

7. **Proof of Address (when the user says they uploaded their document)**
   - Call **extract_proof_of_address('dirk', 'van_dijk')** — same demo documents as above.
   - When it returns successfully, say: "Address Verified! Document accepted."
   - Then if PEP/sanctions/sanctioned-country/fraud/customer-risk results are all clear: "We've completed our checks—you're all set!" If any matches or SBI risk: "We'll need to do a quick review and will be in touch shortly." Do not mention PEP, sanctions, sanctioned country, fraud list, or SBI details.
   - Then say: "Processing your accounts..."
   - For **each** account type the user requested:
     - **SME Business Account**: only if the earlier check_customer_risk result was **not** risk_level **high**—call **create_account(account_type, account_user)** and say "Your SME Business Account has been opened!" If risk_level was **high**, do NOT call create_account for SME; tell the user we cannot open it due to our risk assessment.
     - **Investment Account** and **Personal Current Account**: always call **create_account(account_type, account_user)** then say "Your {account} has been opened!"
   - After all accounts: "You're welcome, {first_name}! Can I help you with anything else today?"

8. **Continued conversation**
   After the closing message, the user can continue chatting. Respond naturally and helpfully.

## Tools (use when appropriate)

- **extract_kyc(first_name, last_name)**: Look up and parse the passport for the given person. The file is resolved automatically from the volume using the naming convention passport_<first_name>_<last_name>.png. Returns first_name, last_name, country, date_of_birth, passport_issue_date, passport_expiry_date, error. Use for identity verification.
- **extract_proof_of_address(first_name, last_name)**: Look up and parse a Proof of Address document for the given person. The file is resolved automatically from the volume using the naming convention utility_bill_<first_name>_<last_name>.png. Returns name, address, document_type, document_date, error.
- **create_account(account_type, account_user)**: Creates a row in the accounts table (id, account_type, account_user). Call once per account **before** saying "Your {account} has been opened!". Use exact account name (e.g. "SME Business Account") and user's full name.
- **check_pep(first_name, last_name, country, date_of_birth)**: Internal—use exact values from extract_kyc. Do not show this result to the user.
- **check_sanctions(first_name, last_name, country, date_of_birth)**: Internal—use exact values from extract_kyc. Do not show this result to the user.
- **check_sanctioned_country(country)**: Internal—check the passport country against the sanctioned countries list (OFAC, EU, UN). Use the country value from extract_kyc. Do not show this result to the user.
- **check_customer_risk(sbi_code)**: Internal—only use when the user is opening an **SME Business Account**. Use the assumed SBI code <DEMO_SBI_CODE> (do not ask the user for SBI). If the result has risk_level **high**, do NOT call create_account for SME Business Account; inform the user we cannot open it. Never call for Personal Current or Investment only. Do not show raw result to the user.
- **check_fraud(first_name, last_name)**: Internal—check person against the shared fraud blacklist (customers/employees; multiple financial institutions). Returns fraud_score (0–100). Use first_name, last_name from extract_kyc. Do not show raw result to the user.

Keep the tone welcoming and on-script.

CRITICAL: Steps 5, 6, and 7 are separate conversational turns. When a step says "STOP here", you MUST end your response and wait for the user's next message. Never combine steps 5+6 or 6+7 into a single response. Step 7 includes account creation and closing—do all of that in one response."""

SYSTEM_PROMPT = (
    SYSTEM_PROMPT
    .replace("<DEMO_SBI_CODE>", DEMO_SBI_CODE)
    .replace("<VOLUME_PATH>", VOLUME_PATH)
)


# ---------------------------------------------------------------------------
# Checkpointer (conversation memory)
# ---------------------------------------------------------------------------
_checkpointer = None


def _get_checkpointer():
    """Return a LangGraph CheckpointSaver backed by Lakebase, or MemorySaver fallback."""
    global _checkpointer
    if _checkpointer is not None:
        return _checkpointer
    if LAKEBASE_INSTANCE_NAME:
        from databricks_langchain import CheckpointSaver

        _checkpointer = CheckpointSaver(instance_name=LAKEBASE_INSTANCE_NAME)
        _checkpointer.setup()
        logger.info("Using Lakebase checkpointer (instance=%s)", LAKEBASE_INSTANCE_NAME)
    else:
        from langgraph.checkpoint.memory import MemorySaver

        _checkpointer = MemorySaver()
        logger.info("Using in-memory checkpointer (no LAKEBASE_INSTANCE_NAME)")
    return _checkpointer


def _get_thread_id(request: "ResponsesAgentRequest") -> str | None:
    """Derive a thread_id for stateful conversations, or None for stateless."""
    # 1. AI Playground / Review App set context.conversation_id
    if hasattr(request, "context") and request.context:
        conv_id = getattr(request.context, "conversation_id", None)
        if conv_id:
            return str(conv_id)
    # 2. Custom frontends pass thread_id in custom_inputs
    if request.custom_inputs:
        tid = request.custom_inputs.get("thread_id")
        if tid:
            return str(tid)
    # 3. Multi-message input → orchestrator sending full history; stay stateless
    if request.input and len(request.input) > 1:
        return None
    # 4. Single message, no thread_id → new conversation
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Lazy-built agent
# ---------------------------------------------------------------------------
_kyc_agent = None


def _get_kyc_agent() -> Any:
    """Build or return the KYC LangChain agent."""
    global _kyc_agent
    if _kyc_agent is not None:
        return _kyc_agent

    from langchain.agents import create_agent
    from langchain_core.tools import tool
    from databricks_langchain import ChatDatabricks, UCFunctionToolkit

    # --- UC function tools (PEP, sanctions, sanctioned countries, SBI risk, fraud) ---
    function_names = [
        f"{CATALOG_SCHEMA}.check_pep",
        f"{CATALOG_SCHEMA}.check_sanctions",
        f"{CATALOG_SCHEMA}.check_sanctioned_country",
        f"{CATALOG_SCHEMA}.check_customer_risk",
        f"{CATALOG_SCHEMA}.check_fraud",
    ]
    uc_toolkit = UCFunctionToolkit(function_names=function_names)
    uc_tools = uc_toolkit.tools

    # --- Python tools (document parsing + account creation via SQL API) ---
    def _normalize_name(name: str) -> str:
        """Lowercase and replace spaces with underscores for file naming."""
        return name.strip().lower().replace(" ", "_")

    @tool
    def extract_kyc(first_name: str, last_name: str) -> str:
        """Parse a passport document for the given person using AI. The file is looked up automatically based on the person's name using the naming convention passport_<first_name>_<last_name>.png in the volume. Returns first_name, last_name, country, date_of_birth, passport_issue_date, passport_expiry_date, and error if any."""
        file_path = f"{VOLUME_PATH}/passport_{_normalize_name(first_name)}_{_normalize_name(last_name)}.png"
        sql = _parse_passport_sql(file_path)
        if sql.startswith("Error:"):
            return sql
        try:
            rows = _execute_sql(sql)
            if not rows:
                return f"No passport found for {first_name} {last_name} at {file_path}."
            return json.dumps(rows[0])
        except Exception as e:
            return f"Parse error: {e}"

    @tool
    def extract_proof_of_address(first_name: str, last_name: str) -> str:
        """Parse a Proof of Address document (utility bill or bank statement) for the given person using AI. The file is looked up automatically based on the person's name using the naming convention utility_bill_<first_name>_<last_name>.png in the volume. Returns name, address, document_type, document_date."""
        file_path = f"{VOLUME_PATH}/utility_bill_{_normalize_name(first_name)}_{_normalize_name(last_name)}.png"
        sql = _parse_document_sql(
            file_path,
            ["name", "address", "document_type", "document_date"],
        )
        if sql.startswith("Error:"):
            return sql
        try:
            rows = _execute_sql(sql)
            if not rows:
                return f"No proof of address found for {first_name} {last_name} at {file_path}."
            return json.dumps(rows[0])
        except Exception as e:
            return f"Parse error: {e}"

    @tool
    def create_account(account_type: str, account_user: str) -> str:
        """Create an account record (ID, account_type, account_user) in the accounts table. Call once per account before saying 'Your {account} has been opened!'. account_type e.g. 'SME Business Account'. account_user is the user's full name."""
        acc_id = str(uuid.uuid4())
        _execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {ACCOUNTS_TABLE} (
                id STRING,
                account_type STRING,
                account_user STRING
            )
        """)
        w = _get_ws_client()
        resp = w.statement_execution.execute_statement(
            warehouse_id=WAREHOUSE_ID,
            statement=f"INSERT INTO {ACCOUNTS_TABLE} (id, account_type, account_user) VALUES (:id, :type, :user)",
            parameters=[
                StatementParameterListItem(name="id", value=acc_id, type="STRING"),
                StatementParameterListItem(name="type", value=account_type, type="STRING"),
                StatementParameterListItem(name="user", value=account_user, type="STRING"),
            ],
            wait_timeout="30s",
        )
        if resp.status.state != StatementState.SUCCEEDED:
            raise RuntimeError(f"INSERT failed: {getattr(resp.status, 'error', None)}")
        return f"Account created: id={acc_id}, type={account_type}, user={account_user}"

    tools = [extract_kyc, extract_proof_of_address, create_account] + uc_tools

    llm_endpoint = os.getenv("LLM_ENDPOINT", "databricks-meta-llama-3-3-70b-instruct")
    llm = ChatDatabricks(endpoint=llm_endpoint, temperature=0.1)
    _kyc_agent = create_agent(
        llm, tools=tools, system_prompt=SYSTEM_PROMPT,
        checkpointer=_get_checkpointer(),
    )
    return _kyc_agent


# ---------------------------------------------------------------------------
# Screening detection helper
# ---------------------------------------------------------------------------
def _screening_has_match(content):
    """Check if a UC screening function (returning TABLE) found any matches.
    Handles JSON list, CSV-in-dict wrapper, and plain CSV formats.
    Returns False for empty results (which still contain column headers)."""
    text = content.strip()
    if not text or text in ("[]", "None", "null", "{}", "''", '""'):
        return False
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return len(parsed) > 0
        if isinstance(parsed, dict):
            val = str(parsed.get("value", parsed.get("result", ""))).strip()
            if not val or val in ("[]", "None", "null"):
                return False
            try:
                inner = json.loads(val)
                if isinstance(inner, list):
                    return len(inner) > 0
            except (json.JSONDecodeError, TypeError):
                pass
            lines = [l for l in val.split("\n") if l.strip()]
            return len(lines) > 1
    except (json.JSONDecodeError, TypeError):
        pass
    lines = [l for l in text.split("\n") if l.strip()]
    return len(lines) > 1


# ---------------------------------------------------------------------------
# Responses API helpers (unchanged)
# ---------------------------------------------------------------------------
def _messages_from_request(input_list: list) -> list:
    """Convert Responses API input (list of dicts with role/content) to LangChain messages."""
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    out = []
    for item in input_list or []:
        role = (item.get("role") or "").lower()
        content = item.get("content") or ""
        if isinstance(content, list):
            content = " ".join(
                c.get("text", "") if isinstance(c, dict) else str(c) for c in content
            )
        if role == "user":
            out.append(HumanMessage(content=content))
        elif role == "assistant":
            out.append(AIMessage(content=content))
        elif role == "system":
            out.append(SystemMessage(content=content))
    return out


def _output_text_item(text: str, item_id: str | None = None) -> dict:
    """Return an OutputItem for the Responses API: type 'message' with content containing output_text."""
    from uuid import uuid4
    return {
        "id": item_id or str(uuid4()),
        "content": [{"type": "output_text", "text": text, "annotations": []}],
        "role": "assistant",
        "type": "message",
    }


# ---------------------------------------------------------------------------
# Responses API handlers
# ---------------------------------------------------------------------------
@invoke()
def invoke_handler(request: ResponsesAgentRequest) -> ResponsesAgentResponse:
    raw = [i.model_dump() if hasattr(i, "model_dump") else (i if isinstance(i, dict) else {"role": "user", "content": str(i)}) for i in (request.input or [])]
    messages = _messages_from_request(raw)
    agent = _get_kyc_agent()

    thread_id = _get_thread_id(request)
    app_id = str(uuid.uuid4())

    with mlflow.start_span(name="kyc_onboarding", span_type="CHAIN") as root:
        # Tag the trace with thread_id so all turns in a conversation can be grouped
        if thread_id:
            mlflow.update_current_trace(tags={"thread_id": thread_id})

        root.set_inputs({
            "application_id": app_id,
            "thread_id": thread_id,
            "message_count": len(messages),
        })

        if thread_id:
            config = {"configurable": {"thread_id": thread_id}}
            result = agent.invoke({"messages": messages}, config=config)
        else:
            result = agent.invoke({"messages": messages})

        new_messages = result.get("messages", [])
        last = new_messages[-1] if new_messages else None
        reply = (last.content if hasattr(last, "content") else str(last)) if last else ""

        # Create execute_tool spans for any tools called
        call_args = {}
        for m in new_messages:
            if getattr(m, "type", None) in ("ai", "assistant"):
                for tc in getattr(m, "tool_calls", []) or []:
                    if tc.get("id"):
                        call_args[tc["id"]] = tc.get("args", {})

        pep_flagged = sanctions_flagged = sanctioned_country_flagged = fraud_flagged = sbi_high_risk = False
        screening_flagged = False
        has_screening = False
        has_create_account = False

        for m in new_messages:
            if getattr(m, "type", None) == "tool":
                name = getattr(m, "name", "")
                content = getattr(m, "content", "") or ""
                if name:
                    args = call_args.get(getattr(m, "tool_call_id", ""), {})
                    with mlflow.start_span(name="execute_tool", span_type="TOOL") as ts:
                        ts.set_attribute("tool.name", name)
                        ts.set_attribute("tool.arguments", json.dumps(args, default=str))
                        ts.set_outputs({"result": content[:4000]})

                    # Screening detection
                    name_lower = name.lower()
                    if "check_pep" in name_lower:
                        has_screening = True
                        if _screening_has_match(content):
                            pep_flagged = screening_flagged = True
                    elif "check_sanctioned_country" in name_lower:
                        has_screening = True
                        if _screening_has_match(content):
                            sanctioned_country_flagged = screening_flagged = True
                    elif "check_sanctions" in name_lower:
                        has_screening = True
                        if _screening_has_match(content):
                            sanctions_flagged = screening_flagged = True
                    elif "check_fraud" in name_lower:
                        has_screening = True
                        m_fraud = re.search(r'fraud_score["\']?\s*[:=]\s*(\d+)', content)
                        if m_fraud and int(m_fraud.group(1)) > 0:
                            fraud_flagged = screening_flagged = True
                    elif "customer_risk" in name_lower:
                        has_screening = True
                        if "high" in content.lower():
                            sbi_high_risk = True
                    elif "create_account" in name_lower:
                        has_create_account = True

        # Create kyc_decision span if screening results or account creation detected
        if has_screening or has_create_account:
            if screening_flagged:
                decision_type = "refer"
            elif sbi_high_risk:
                decision_type = "conditional"
            else:
                decision_type = "approved"

            tags = []
            if has_screening:
                tags.append(f"pep:{'match' if pep_flagged else 'clear'}")
                tags.append(f"sanctions:{'match' if sanctions_flagged else 'clear'}")
                tags.append(f"sanctioned_country:{'match' if sanctioned_country_flagged else 'clear'}")
                tags.append(f"fraud:{'match' if fraud_flagged else 'clear'}")
            if sbi_high_risk:
                tags.append("sbi_risk:high")
            tags.append(f"decision:{decision_type}")

            reasoning = f"Turn-level decision: {decision_type}."
            if pep_flagged:
                reasoning += " PEP match detected."
            if sanctions_flagged:
                reasoning += " Sanctions match detected."
            if sanctioned_country_flagged:
                reasoning += " Sanctioned country detected."
            if fraud_flagged:
                reasoning += " Fraud flag raised."
            if sbi_high_risk:
                reasoning += " High SBI risk."
            if not screening_flagged and not sbi_high_risk:
                reasoning += " All checks clear."

            with mlflow.start_span(name="kyc_decision", span_type="AGENT") as dec:
                dec.set_inputs({
                    "application_id": app_id,
                    "screening_flagged": screening_flagged,
                    "pep_match": pep_flagged,
                    "sanctions_match": sanctions_flagged,
                    "sanctioned_country_match": sanctioned_country_flagged,
                    "fraud_match": fraud_flagged,
                    "sbi_high_risk": sbi_high_risk,
                })
                dec.set_outputs({
                    "decision_type": decision_type,
                    "confidence_score": 1.0,
                    "reasoning": reasoning,
                    "fingerprint_tags": tags,
                })

        root.set_outputs({
            "application_id": app_id,
            "reply": reply[:500],
        })

    # Collect tool calls with names and abbreviated results for the frontend
    tool_calls_info = []
    for m in new_messages:
        if getattr(m, "type", None) == "tool":
            name = getattr(m, "name", "")
            content = getattr(m, "content", "") or ""
            if name:
                # Parse tool result into a dict if possible
                try:
                    parsed_result = json.loads(content)
                except (json.JSONDecodeError, ValueError):
                    parsed_result = content[:500]
                tool_calls_info.append({"name": name, "result": parsed_result})

    custom_outputs = {}
    if thread_id:
        custom_outputs["thread_id"] = thread_id
    if tool_calls_info:
        custom_outputs["tool_calls"] = tool_calls_info

    return ResponsesAgentResponse(
        output=[_output_text_item(reply)],
        custom_outputs=custom_outputs,
    )


@stream()
async def stream_handler(request: ResponsesAgentRequest):
    """Non-streaming fallback: invoke and yield a single event."""
    response = invoke_handler(request)
    raw_item = response.output[0] if response.output else _output_text_item("")
    item = raw_item.model_dump() if hasattr(raw_item, "model_dump") else dict(raw_item)
    if response.custom_outputs:
        item["custom_outputs"] = response.custom_outputs
    yield ResponsesAgentStreamEvent(type="response.output_item.done", item=item)
