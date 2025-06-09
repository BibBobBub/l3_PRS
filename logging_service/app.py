from flask import Flask, request, jsonify
import os
import random
import json
import requests

app = Flask(__name__)

STORAGE_FILE = '/shared/logs.json'
HAZELCAST_HOSTS = os.getenv('HAZELCAST_HOSTS', 'localhost').split(',')
MAP = 'messages'


def save_logs(uuid):
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    data[uuid] = uuid

    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f)


def put_message(host, uuid, msg):
    url = f"http://{host}:5701/hazelcast/rest/maps/{MAP}/{uuid}"
    response = requests.put(url, data=msg)
    app.logger.info(f"[PUT] {uuid} to {host}")
    save_logs(uuid)
    return response.text


def curl_get(url, timeout=2):
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return response.text
        return None
    except requests.RequestException:
        return None


def get_all_messages(host):
    if not os.path.exists(STORAGE_FILE):
        return jsonify([])

    with open(STORAGE_FILE, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return jsonify([])

    messages = []
    for uuid in data.keys():
        url = f"http://{host}:5701/hazelcast/rest/maps/{MAP}/{uuid}"
        app.logger.info(f"[GETTING] {uuid} FROM {host} URL {url}")
        value = curl_get(url, timeout=2)
        app.logger.info(f"[GET] {uuid} FROM {host} VALUE {value if value else 'NOT FOUND'}")
        if value:
            messages.append({uuid: value})
    return jsonify(messages)


@app.route('/log', methods=['POST'])
def log():
    data = request.get_json()
    if not data or 'uuid' not in data or 'msg' not in data:
        return 'Bad Request', 400
    target = random.choice(HAZELCAST_HOSTS)
    return put_message(target, data['uuid'], data['msg'])


@app.route('/logs', methods=['GET'])
def logs():
    target = random.choice(HAZELCAST_HOSTS)
    return get_all_messages(target)


@app.errorhandler(404)
def not_found(_):
    return "Not Found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
