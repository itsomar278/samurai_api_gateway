from flask import Flask, request, jsonify, Response

from utils import jwt_utils
from utils.rabbitmq_utils import RabbitMQ, generate_message
import requests
import jwt

app = Flask(__name__)

UNAUTHENTICATED_ENDPOINTS = ['/login', '/signup']
rabbitmq = RabbitMQ()


def validate_request_data(required_fields, data):
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")


@app.before_request
def authenticate_request():
    if request.path in UNAUTHENTICATED_ENDPOINTS:
        return

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    if not jwt_utils.is_authenticated(token):
        return jsonify({"error": "Invalid or expired token"}), 401


@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.json.get('email')
        password = request.json.get('password')

        response = requests.post(
            "http://127.0.0.1:8000/api/accounts/login/",
            json={"email": email, "password": password}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": f"Auth service unavailable: {str(e)}"}), 503


@app.route('/signup', methods=['POST'])
def signup():
    try:
        email = request.json.get('email')
        password = request.json.get('password')
        first_name = request.json.get('first_name')
        last_name = request.json.get('last_name')

        response = requests.post(
            "http://127.0.0.1:8000/api/accounts/register/",
            json={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name
            }
        )

        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": f"Auth service unavailable: {str(e)}"}), 503


@app.route('/process', methods=['POST'])
def process_youtube_link():
    data = request.json
    queue_name = "video_translation"
    token = request.headers.get('Authorization')
    payload = jwt_utils.decode_jwt_payload(token)
    user_id = payload['user_id']
    start_minute = data.get('start_minute', 0)
    end_minute = data.get('end_minute')
    video_url = data.get('video_url')

    if not video_url or not end_minute:
        return jsonify({"error": "Missing required fields:  video_url , end_minute"}), 400

    try:
        message = generate_message(user_id, start_minute, end_minute, video_url)
        rabbitmq.publish_message(queue_name, message)
        return jsonify({"status": "Processing started", "request_id": message["request_id"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/translation_status', methods=['GET'])
def translation_status():
    request_id = request.args.get('request_id')
    user_id = request.args.get('user_id')

    if not request_id or not user_id:
        return jsonify({"error": "Both 'request_id' and 'user_id' are required as query parameters."}), 400

    try:
        response = requests.get(f"http://127.0.0.1:5050/api/transclation-status/?request_id={request_id}&user_id={user_id}")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": f"Error communicating with translation service: {str(e)}"}), 503


@app.route('/translations_by_user', methods=['GET'])
def translations_by_user():
    token = request.headers.get('Authorization')
    payload = jwt_utils.decode_jwt_payload(token)
    user_id = payload['user_id']

    if not user_id:
        return jsonify({"error": "User ID is required as a query parameter."}), 400

    try:
        response = requests.get(f"http://127.0.0.1:5050/api/transclation-status-by-user-id/?user_id={user_id}")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": f"Error communicating with translation service: {str(e)}"}), 503


@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    try:
        required_fields = ['selected_index', 'user_id', 'total_questions', 'hard_questions']
        validate_request_data(required_fields, request.json)

        response = requests.post(
            "http://127.0.0.1:8080/interact/generate-quiz/",
            json=request.json
        )
        return response.json(), response.status_code
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except requests.RequestException as e:
        return jsonify({"error": f"Error communicating with quiz service: {str(e)}"}), 503


@app.route('/chat-with-content', methods=['POST'])
def chat_with_content():
    try:
        required_fields = ['selected_index', 'user_id', 'user_query','chat_history']
        validate_request_data(required_fields, request.json)

        response = requests.post(
            "http://127.0.0.1:8080/interact/chat-with-content/",
            json=request.json
        )
        return response.json(), response.status_code
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except requests.RequestException as e:
        return jsonify({"error": f"Error communicating with chat service: {str(e)}"}), 503


@app.route('/generate-summary', methods=['POST'])
def generate_summary():
    try:
        required_fields = ['selected_index', 'user_id', 'summary_length']
        validate_request_data(required_fields, request.json)

        response = requests.post(
            "http://127.0.0.1:8080/interact/generate-summary/",
            json=request.json
        )
        return response.json(), response.status_code
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except requests.RequestException as e:
        return jsonify({"error": f"Error communicating with summary service: {str(e)}"}), 503


@app.route('/convert-to-article', methods=['POST'])
def convert_to_article():
    try:
        required_fields = ['selected_index', 'user_id']
        validate_request_data(required_fields, request.json)

        response = requests.post(
            "http://127.0.0.1:8080/interact/convert-to-article/",
            json=request.json
        )

        return Response(
            response.text,
            status=response.status_code,
            mimetype='text/markdown'
        )
    except ValueError as e:
        return str(e), 400
    except requests.RequestException as e:
        return f"Error communicating with article conversion service: {str(e)}", 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
