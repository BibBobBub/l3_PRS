from flask import Flask, request, jsonify
import requests
import uuid
import random

app = Flask(__name__)

LOGGING_SERVICES = [
    "http://logging-service-1:5001",
    "http://logging-service-2:5001",
    "http://logging-service-3:5001"
]

MESSAGES_URL = 'http://messages-service:5004/message'  # messages-service assumed on 5004

@app.route('/message', methods=['POST'])
def handle_post():
    data = request.get_json()
    msg = data.get('msg')
    if not msg:
        return jsonify({'error': 'Missing msg'}), 400

    msg_id = str(uuid.uuid4())
    payload = {'uuid': msg_id, 'msg': msg}
    logging_url = random.choice(LOGGING_SERVICES) + "/log"
    try:
        requests.post(logging_url, json=payload)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'status': 'Message forwarded', 'uuid': msg_id}), 200

@app.route('/message', methods=['GET'])
def handle_get():
    logging_url = random.choice(LOGGING_SERVICES) + "/log"
    try:
        log_resp = requests.get(logging_url)
        msg_resp = requests.get(MESSAGES_URL)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    combined = f"{log_resp.text}\n{msg_resp.text}"
    return combined, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)