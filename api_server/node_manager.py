import uuid
import time
import subprocess
import logging
from utils.models import Node, Pod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeManager:
    def __init__(self):
        self.nodes = {}  # Dictionary to store node objects: {node_id: Node}
        self.pods = {}   # Dictionary to store pod objects: {pod_id: Pod}
    
    def add_node(self, cpu_cores):
        """
        Add a new node to the cluster
        
        Args:
            cpu_cores (int): Number of CPU cores available on the node
            
        Returns:
            str: ID of the newly created node
        """
        try:
            # Generate a unique ID for the node
            node_id = str(uuid.uuid4())
            
            # Launch Docker container to simulate the node
            container_name = f"node_{node_id[:8]}"
            
            # Launch Docker container
            cmd = [
                "docker", "run", "-d",
                "--name", container_name,
                "-e", f"NODE_ID={node_id}",
                "-e", f"CPU_CORES={cpu_cores}",
                "-e", "API_SERVER=http://host.docker.internal:5000",
                "--add-host", "host.docker.internal:host-gateway",
                "node-agent"  # Docker image name
            ]
            
            # This is a simulation, so we'll comment out the actual Docker commands
            # subprocess.run(cmd, check=True)
            logger.info(f"Would launch container with command: {' '.join(cmd)}")
            
            # Create node object and store it
            node = Node(
                id=node_id,
                cpu_cores=cpu_cores,
                available_cores=cpu_cores,
                status="HEALTHY",
                last_heartbeat=time.time(),
                pods=[]
            )
            
            self.nodes[node_id] = node
            logger.info(f"Added node {node_id} with {cpu_cores} CPU cores")
            
            return node_id
            
        except Exception as e:
            logger.error(f"Failed to add node: {str(e)}")
            raise Exception(f"Failed to add node: {str(e)}")
    
    def list_nodes(self):
        """
        List all nodes and their status
        
        Returns:
            list: List of dictionaries containing node information
        """
        return [node.to_dict() for node in self.nodes.values()]
    
    def get_node(self, node_id):
        """
        Get a node by ID
        
        Args:
            node_id (str): ID of the node
            
        Returns:
            Node: Node object if found, None otherwise
        """
        return self.nodes.get(node_id)
    
    def update_node_status(self, node_id, status):
        """
        Update the status of a node
        
        Args:
            node_id (str): ID of the node
            status (str): New status of the node (HEALTHY, UNHEALTHY, etc.)
        """
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            logger.info(f"Updated node {node_id} status to {status}")
        else:
            logger.warning(f"Attempted to update non-existent node {node_id}")
    
    def update_node_heartbeat(self, node_id):
        """
        Update the last heartbeat time for a node
        
        Args:
            node_id (str): ID of the node
        """
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = time.time()
            self.nodes[node_id].status = "HEALTHY"
        else:
            logger.warning(f"Received heartbeat for non-existent node {node_id}")
    
    def get_available_nodes(self):
        """
        Get all healthy nodes with their available resources
        
        Returns:
            list: List of nodes that are healthy
        """
        return [node for node in self.nodes.values() if node.status == "HEALTHY"]
    
    def add_pod_to_node(self, node_id, pod_id, cpu_required):
        """
        Add a pod to a node
        
        Args:
            node_id (str): ID of the node
            pod_id (str): ID of the pod
            cpu_required (int): CPU cores required by the pod
            
        Returns:
            bool: True if pod was added successfully, False otherwise
        """
        if node_id not in self.nodes:
            logger.warning(f"Attempted to add pod to non-existent node {node_id}")
            return False
        
        node = self.nodes[node_id]
        
        if node.available_cores < cpu_required:
            logger.warning(f"Node {node_id} does not have enough resources for pod {pod_id}")
            return False
        
        # Update node resources
        node.available_cores -= cpu_required
        node.pods.append(pod_id)
        
        # Create and store pod
        pod = Pod(
            id=pod_id,
            node_id=node_id,
            cpu_required=cpu_required,
            status="RUNNING"
        )
        self.pods[pod_id] = pod
        
        logger.info(f"Added pod {pod_id} to node {node_id}")
        return True
    
    def get_pod(self, pod_id):
        """
        Get a pod by ID
        
        Args:
            pod_id (str): ID of the pod
            
        Returns:
            Pod: Pod object if found, None otherwise
        """
        return self.pods.get(pod_id)
    
    def list_pods(self):
        """
        List all pods
        
        Returns:
            list: List of dictionaries containing pod information
        """
        return [pod.to_dict() for pod in self.pods.values()]
    
    def handle_node_failure(self, node_id):
        """
        Handle node failure by marking all pods on the node as FAILED
        and recovering them on other nodes if possible
        
        Args:
            node_id (str): ID of the failed node
        """
        if node_id not in self.nodes:
            logger.warning(f"Attempted to handle failure for non-existent node {node_id}")
            return
        
        node = self.nodes[node_id]
        node.status = "FAILED"
        
        # Get all pods running on the failed node
        failed_pods = [pod_id for pod_id in node.pods]
        
        logger.info(f"Node {node_id} failed with {len(failed_pods)} pods")
        
        # Mark all pods on the node as FAILED
        for pod_id in failed_pods:
            if pod_id in self.pods:
                self.pods[pod_id].status = "FAILED"
        
        return failed_pods