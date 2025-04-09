import argparse
import requests
import json
from tabulate import tabulate
import sys

class ClusterClient:
    def __init__(self, api_server="http://localhost:5050"):
        self.api_server = api_server
    
    def add_node(self, cpu_cores):
        """Add a new node to the cluster"""
        try:
            response = requests.post(
                f"{self.api_server}/api/nodes",
                json={"cpu_cores": cpu_cores}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Node added successfully with ID: {data['node_id']}")
            else:
                print(f"Failed to add node: {response.text}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def list_nodes(self):
        """List all nodes and their health status"""
        try:
            response = requests.get(f"{self.api_server}/api/nodes")
            
            if response.status_code == 200:
                nodes = response.json()["nodes"]
                if not nodes:
                    print("No nodes found in the cluster.")
                    return
                
                # Format the data for tabulate
                headers = ["Node ID", "CPU Cores", "Available Cores", "Status", "Pod Count"]
                table_data = []
                
                for node in nodes:
                    table_data.append([
                        node["id"][:8] + "...",  # Truncate ID for display
                        node["cpu_cores"],
                        node["available_cores"],
                        node["status"],
                        node["pod_count"]
                    ])
                
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print(f"Failed to list nodes: {response.text}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def launch_pod(self, cpu_required):
        """Launch a new pod with specified CPU requirements"""
        try:
            response = requests.post(
                f"{self.api_server}/api/pods",
                json={"cpu_required": cpu_required}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Pod launched successfully with ID: {data['pod_id']}")
                print(f"Allocated to node: {data['node_id']}")
            else:
                print(f"Failed to launch pod: {response.text}")
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Kubernetes-like Cluster Simulation Client")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add node command
    add_node_parser = subparsers.add_parser("add-node", help="Add a new node to the cluster")
    add_node_parser.add_argument("--cpu", type=int, required=True, help="Number of CPU cores")
    
    # List nodes command
    subparsers.add_parser("list-nodes", help="List all nodes and their health status")
    
    # Launch pod command
    launch_pod_parser = subparsers.add_parser("launch-pod", help="Launch a new pod")
    launch_pod_parser.add_argument("--cpu", type=int, required=True, help="CPU cores required")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize client
    client = ClusterClient()
    
    # Execute command
    if args.command == "add-node":
        client.add_node(args.cpu)
    elif args.command == "list-nodes":
        client.list_nodes()
    elif args.command == "launch-pod":
        client.launch_pod(args.cpu)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()