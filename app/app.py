from flask import Flask, send_from_directory, request, jsonify
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Genie configuration — values injected at deploy time via databricks.yml.
# DATABRICKS_HOST is auto-set by the Databricks Apps platform; SDK auto-detects when None.
DATABRICKS_HOST = os.getenv('DATABRICKS_HOST')
GENIE_SPACE_ID = os.getenv('GENIE_SPACE_ID', '')
DASHBOARD_EMBED_URL = os.getenv('DASHBOARD_EMBED_URL', '')

flask_app = Flask(__name__)

# Initialize Databricks SDK with Service Principal
from databricks.sdk import WorkspaceClient
from databricks.sdk.config import Config

def get_sp_client():
    """Get Databricks client authenticated as Service Principal"""
    try:
        # In a Databricks App, DATABRICKS_HOST is auto-set by the platform; SDK resolves auth.
        return WorkspaceClient(config=Config(host=DATABRICKS_HOST)) if DATABRICKS_HOST else WorkspaceClient()
    except Exception as e:
        print(f"Error creating SP client: {e}")
        return None

def get_user_email():
    return request.headers.get('X-Forwarded-Email')

# ============== Static File Routes ==============

@flask_app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'demo-navigation.html')

@flask_app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory(BASE_DIR, filename)

@flask_app.route('/health')
def health():
    return 'ok', 200

@flask_app.route('/metrics')
def metrics():
    return 'ok', 200

# ============== Genie API Proxy Routes ==============

@flask_app.route('/api/genie/config')
def genie_config():
    sp_client = get_sp_client()
    return jsonify({
        'configured': bool(sp_client),
        'workspace': DATABRICKS_HOST,
        'space_id': GENIE_SPACE_ID,
        'dashboard_url': DASHBOARD_EMBED_URL,
        'user': get_user_email(),
        'has_sp_client': bool(sp_client)
    })

@flask_app.route('/api/genie/start-conversation', methods=['POST'])
def start_conversation():
    """Start a new Genie conversation"""
    try:
        client = get_sp_client()
        if not client:
            return jsonify({'error': 'No SDK client available'}), 500
        
        # Get initial message from request (or use default)
        data = request.get_json() or {}
        content = data.get('content', 'Hello')
        
        # Per API docs: content is required to start conversation
        result = client.api_client.do(
            'POST',
            f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/start-conversation',
            body={'content': content}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flask_app.route('/api/genie/conversations/<conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """Send a message to Genie"""
    try:
        client = get_sp_client()
        if not client:
            return jsonify({'error': 'No SDK client available'}), 500
        
        data = request.get_json()
        content = data.get('content', '')
        
        result = client.api_client.do(
            'POST',
            f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages',
            body={'content': content}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flask_app.route('/api/genie/conversations/<conversation_id>/messages/<message_id>', methods=['GET'])
def get_message(conversation_id, message_id):
    """Get a message response from Genie"""
    try:
        client = get_sp_client()
        if not client:
            return jsonify({'error': 'No SDK client available'}), 500
        
        result = client.api_client.do(
            'GET',
            f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}'
        )
        
        # Log full response structure for debugging
        logger.info(f"Full message response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        logger.info(f"Message status: {result.get('status')}")
        logger.info(f"Full attachments array: {result.get('attachments')}")
        
        # If status is COMPLETED or EXECUTING_QUERY and there are attachments with queries,
        # fetch the query results
        if result.get('status') in ['COMPLETED', 'EXECUTING_QUERY']:
            attachments = result.get('attachments') or []
            logger.info(f"Message status: {result.get('status')}, attachments count: {len(attachments)}")
            
            for attachment in attachments:
                # Log full attachment structure to see what fields are available
                logger.info(f"Attachment full structure: {attachment}")
                logger.info(f"Attachment keys: {list(attachment.keys()) if isinstance(attachment, dict) else 'Not a dict'}")
                
                # Try different possible ID fields
                attachment_id = (
                    attachment.get('id') or 
                    attachment.get('attachment_id') or 
                    attachment.get('query', {}).get('id') or
                    attachment.get('query', {}).get('attachment_id')
                )
                
                logger.info(f"Attachment: id={attachment_id}, has_query={bool(attachment.get('query'))}")
                
                if attachment.get('query'):
                    query_sql = attachment.get('query', {}).get('query', '')
                    
                    if not attachment_id:
                        logger.error(f"Query attachment found but no ID available! Attachment structure: {attachment}")
                        # Try to get query result anyway - maybe Genie auto-executes and we can get it without ID
                        # Or maybe the ID is in the query object itself
                        query_obj = attachment.get('query', {})
                        attachment_id = query_obj.get('id') or query_obj.get('attachment_id')
                        
                        if not attachment_id:
                            logger.error(f"Still no ID found. Query object: {query_obj}")
                            attachment['query_result_error'] = 'Attachment ID not found in response'
                            continue
                        else:
                            logger.info(f"Found attachment ID in query object: {attachment_id}")
                    
                    logger.info(f"Found query attachment {attachment_id} with SQL: {query_sql[:100]}...")
                    
                    try:
                        # First try to GET existing query result (Genie might auto-execute)
                        logger.info(f"Trying to GET query-result for attachment {attachment_id}")
                        try:
                            query_result = client.api_client.do(
                                'GET',
                                f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}/query-result'
                            )
                            logger.info(f"Successfully got query-result without executing")
                            attachment['query_result'] = query_result
                            continue  # Skip execute-query if we got results
                        except Exception as get_err:
                            logger.info(f"GET query-result failed (might need to execute): {get_err}")
                        
                        # If GET failed, try to execute the query
                        logger.info(f"Executing query for attachment {attachment_id}")
                        exec_result = client.api_client.do(
                            'POST',
                            f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}/execute-query'
                        )
                        logger.info(f"execute-query response keys: {exec_result.keys() if exec_result else 'None'}")
                        
                        # Log full response for debugging
                        logger.info(f"execute-query full response: {exec_result}")
                        
                        # Check execution status - response structure may vary
                        stmt_resp = exec_result.get('statement_response', exec_result)
                        stmt_status = stmt_resp.get('status', {}) if isinstance(stmt_resp, dict) else {}
                        state = stmt_status.get('state', 'UNKNOWN') if isinstance(stmt_status, dict) else 'UNKNOWN'
                        
                        # Also check if result is already in response
                        has_result_data = bool(stmt_resp.get('result', {}).get('data_array') if isinstance(stmt_resp, dict) else False)
                        
                        logger.info(f"Query execution state: {state}, has_result_data: {has_result_data}")
                        
                        if state == 'SUCCEEDED' or has_result_data:
                            # Query succeeded - attach the result
                            attachment['query_result'] = exec_result
                            logger.info(f"Query executed successfully, attached result")
                        elif state in ['PENDING', 'RUNNING']:
                            # Query still running - poll for result
                            logger.info(f"Query still {state}, will need to poll")
                            attachment['query_result'] = exec_result
                            attachment['query_status'] = state
                        else:
                            # Query failed or other state
                            error_msg = stmt_status.get('error', {}).get('message', 'Unknown error') if isinstance(stmt_status, dict) else str(stmt_status)
                            logger.error(f"Query execution failed: {error_msg}, full status: {stmt_status}")
                            attachment['query_result_error'] = error_msg
                            attachment['query_result'] = exec_result
                            
                    except Exception as ee:
                        logger.error(f"Error executing query: {ee}")
                        # Fallback: try to get existing result
                        try:
                            logger.info(f"Trying to get existing query-result as fallback")
                            query_result = client.api_client.do(
                                'GET',
                                f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}/query-result'
                            )
                            attachment['query_result'] = query_result
                            logger.info(f"Got existing query-result")
                        except Exception as qe:
                            logger.error(f"Both execute and get failed: exec={ee}, get={qe}")
                            attachment['query_result_error'] = f"execute: {ee}, get: {qe}"
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flask_app.route('/api/genie/debug/<conversation_id>/<message_id>')
def debug_message(conversation_id, message_id):
    """Debug endpoint to see raw Genie response"""
    try:
        client = get_sp_client()
        if not client:
            return jsonify({'error': 'No SDK client available'}), 500
        
        # Get message
        result = client.api_client.do(
            'GET',
            f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}'
        )
        
        debug_info = {
            'message_status': result.get('status'),
            'attachments_count': len(result.get('attachments') or []),
            'full_message_response': result,  # Include full response
        }
        
        # Try to get query result for first attachment with query
        attachments = result.get('attachments') or []
        for att in attachments:
            if att.get('query'):
                att_id = att.get('id')
                debug_info['attachment_id'] = att_id
                debug_info['attachment_keys'] = list(att.keys())
                debug_info['attachment_full'] = att  # Include full attachment
                
                if att_id:
                    # Try execute-query
                    try:
                        logger.info(f"DEBUG: Executing query for attachment {att_id}")
                        exec_resp = client.api_client.do(
                            'POST',
                            f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}/attachments/{att_id}/execute-query'
                        )
                        debug_info['execute_query_response'] = exec_resp
                        logger.info(f"DEBUG: execute-query response: {exec_resp}")
                    except Exception as e:
                        debug_info['execute_query_error'] = str(e)
                        logger.error(f"DEBUG: execute-query error: {e}")
                    
                    # Try get query-result
                    try:
                        qr = client.api_client.do(
                            'GET',
                            f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}/attachments/{att_id}/query-result'
                        )
                        debug_info['query_result_raw'] = qr
                        logger.info(f"DEBUG: query-result response: {qr}")
                    except Exception as e:
                        debug_info['query_result_error'] = str(e)
                        logger.error(f"DEBUG: query-result error: {e}")
                break
        
        return jsonify(debug_info)
    except Exception as e:
        logger.error(f"DEBUG endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    flask_app.run(debug=True)
