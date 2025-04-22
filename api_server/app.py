from flask import Flask, request, jsonify
import threading
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


@app.route('/')
def home():
    return "✅ Cluster Simulation API is running. Use /api/add_node, /api/launch_pod, /api/nodes, /api/pods, /api/heartbeat."


@app.route('/api/nodes', methods=['GET'])
def list_nodes():
    nodes = node_manager.list_nodes()
    return jsonify({"nodes": nodes})


@app.route('/api/nodes', methods=['POST'])
def add_node():
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
    try:
        health_monitor.process_heartbeat(node_id)
        return jsonify({"status": "Heartbeat received"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/nodes/view", methods=["GET"])
def view_nodes():
    node_list = [node.to_dict() for node in node_manager.get_nodes().values()]
    html = """
    <html>
    <head>
        <title>Cluster Nodes</title>
        <style>
            table {
                width: 90%;
                border-collapse: collapse;
                margin: 20px auto;
                font-family: Arial, sans-serif;
            }
            th, td {
                padding: 10px;
                border: 1px solid #ccc;
                text-align: center;
            }
            th {
                background-color: #e0f7fa;
            }
            h1 {
                text-align: center;
                font-family: Arial, sans-serif;
            }
        </style>
    </head>
    <body>
        <h1>Cluster Nodes</h1>
        <table>
            <tr>
                <th>Node ID</th>
                <th>Total CPU</th>
                <th>Available CPU</th>
                <th>Status</th>
                <th>Pods</th>
                <th>Last Heartbeat</th>
                <th>Container ID</th>
            </tr>
    """
    for node in node_list:
        html += f"""
            <tr>
                <td>{node['id']}</td>
                <td>{node['cpu_total']}</td>
                <td>{node['cpu_available']}</td>
                <td>{node['status']}</td>
                <td>{", ".join(node['pods']) if node['pods'] else "None"}</td>
                <td>{node['last_heartbeat']:.2f}</td>
                <td>{node['container_id']}</td>
            </tr>
        """
    html += """
        </table>
    </body>
    </html>
    """
    return html


@app.route("/api/pods/view", methods=["GET"])
def view_pods():
    pod_list = [pod.to_dict() for pod in pod_scheduler.get_pods().values()]
    html = """
    <html>
    <head>
        <title>Launched Pods</title>
        <style>
            table {
                width: 80%;
                border-collapse: collapse;
                margin: 20px auto;
                font-family: Arial, sans-serif;
            }
            th, td {
                padding: 10px;
                border: 1px solid #ccc;
                text-align: center;
            }
            th {
                background-color: #f2f2f2;
            }
            h1 {
                text-align: center;
                font-family: Arial, sans-serif;
            }
        </style>
    </head>
    <body>
        <h1>Launched Pods</h1>
        <table>
            <tr>
                <th>Pod ID</th>
                <th>CPU Required</th>
                <th>Assigned Node</th>
            </tr>
    """
    for pod in pod_list:
        html += f"""
            <tr>
                <td>{pod['id']}</td>
                <td>{pod['cpu_required']}</td>
                <td>{pod['assigned_node']}</td>
            </tr>
        """
    html += """
        </table>
    </body>
    </html>
    """
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
