from flask import Flask, request, jsonify
import hazelcast
import os

app = Flask(__name__)

# Hazelcast Client Setup
'''
hz_client = hazelcast.HazelcastClient(
    cluster_members=[("your_hazelcast_host", 5701)]  # Replace with your Hazelcast server host and port
)
'''
#hz_client = hazelcast.HazelcastClient(hazelcast)
hz_client = hazelcast.HazelcastClient(
    cluster_members=["172.25.0.2:5701"]  # Replace with your Hazelcast server host and port
)
msg_map = hz_client.get_map("messages").blocking()

@app.route('/log', methods=['POST'])
def save_log():
    data = request.get_json()
    uuid = data.get('uuid')
    msg = data.get('msg')
    if uuid and msg:
        msg_map.put(uuid, msg)
        print(f"[LOGGING-{os.environ.get('INSTANCE_NAME', 'default')}] Received: {uuid} -> {msg}")
        return jsonify({'status': 'stored'}), 200
    return jsonify({'error': 'Missing data'}), 400

@app.route('/log', methods=['GET'])
def get_logs():
    values = msg_map.values()
    return '\n'.join(values), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001)#int(os.environ.get('PORT', 5001)))
