"""Start the KYC agent server (Responses API on /invocations)."""
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)

# Set MLflow trace destination so export includes experiment_id
import os
_experiment_id = os.environ.get("MLFLOW_EXPERIMENT_ID")
if _experiment_id:
    import logging as _logging
    import mlflow
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "databricks"))
    try:
        mlflow.set_experiment(experiment_id=_experiment_id)
        from mlflow.tracing import set_destination
        try:
            from mlflow.entities.trace_location import MlflowExperimentLocation
            set_destination(MlflowExperimentLocation(experiment_id=_experiment_id))
        except ImportError:
            from mlflow.tracing.destination import MlflowExperiment
            set_destination(MlflowExperiment(experiment_id=_experiment_id))
    except Exception as e:
        _logging.getLogger(__name__).warning(
            "Could not configure MLflow experiment for tracing: %s. "
            "Traces will not be exported. Create the experiment first and grant "
            "the app service principal CAN MANAGE permission.", e,
        )

import agent_server.agent  # noqa: E402 - register invoke/stream handlers

from pathlib import Path
from mlflow.genai.agent_server import AgentServer
from starlette.responses import HTMLResponse

agent_server = AgentServer("ResponsesAgent", enable_chat_proxy=True)
app = agent_server.app

_chat_html = (Path(__file__).parent / "chat.html").read_text()


@app.get("/", response_class=HTMLResponse)
async def chat_ui():
    return _chat_html


def main():
    agent_server.run(app_import_string="agent_server.start_server:app")
