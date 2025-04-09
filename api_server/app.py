from flask import Flask, request, jsonify
import threading
import time
from api_server.node_manager import NodeManager
from api_server.pod_scheduler import PodScheduler
from api_server.health_monitor import HealthMonitor

app = Flask(__name__)

# Initialize components
node_manager = NodeManager()
pod_scheduler = PodScheduler(node_manager)
health_monitor = HealthMonitor(node_manager)

# Start health monitoring in a separate thread
monitoring_thread = threading.Thread(target=health_monitor.start_monitoring, daemon=True)
monitoring_thread.start()

@app.route('/api/nodes', methods=['GET'])
def list_nodes():
    """List all nodes and their health status"""
    nodes = node_manager.list_nodes()
    return jsonify({"nodes": nodes})

@app.route('/api/nodes', methods=['POST'])
def add_node():
    """Add a new node to the cluster"""
    data = request.json
    if not data or 'cpu_cores' not in data:
        return jsonify({"error": "CPU cores must be specified"}), 400
    
    try:
        node_id = node_manager.add_node(data['cpu_cores'])
        return jsonify({"message": "Node added successfully", "node_id": node_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pods', methods=['POST'])
def launch_pod():
    """Launch a new pod with specified CPU requirements"""
    data = request.json
    if not data or 'cpu_required' not in data:
        return jsonify({"error": "CPU requirements must be specified"}), 400
    
    try:
        result = pod_scheduler.schedule_pod(data['cpu_required'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/nodes/<node_id>/heartbeat', methods=['POST'])
def receive_heartbeat(node_id):
    """Receive heartbeat from a node"""
    try:
        health_monitor.process_heartbeat(node_id)
        return jsonify({"status": "Heartbeat received"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)