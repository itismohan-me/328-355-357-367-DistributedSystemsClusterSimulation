import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PodScheduler:
    def __init__(self, node_manager):
        self.node_manager = node_manager
        self.scheduling_algorithm = "first-fit"  # Default algorithm
    
    def set_scheduling_algorithm(self, algorithm):
        """
        Set the scheduling algorithm to use
        
        Args:
            algorithm (str): The algorithm to use ('first-fit', 'best-fit', or 'worst-fit')
        """
        valid_algorithms = ["first-fit", "best-fit", "worst-fit"]
        if algorithm not in valid_algorithms:
            raise ValueError(f"Invalid scheduling algorithm. Choose from: {valid_algorithms}")
        
        self.scheduling_algorithm = algorithm
        logger.info(f"Scheduling algorithm set to: {algorithm}")
    
    def schedule_pod(self, cpu_required):
        """
        Schedule a pod on a node using the specified algorithm
        
        Args:
            cpu_required (int): CPU cores required by the pod
            
        Returns:
            dict: Dictionary containing pod_id and node_id if scheduled successfully
            
        Raises:
            Exception: If no suitable node is found
        """
        # Generate a unique ID for the pod
        pod_id = str(uuid.uuid4())
        
        # Get all available (healthy) nodes
        available_nodes = self.node_manager.get_available_nodes()
        
        if not available_nodes:
            logger.warning("No healthy nodes available for scheduling")
            raise Exception("No healthy nodes available for scheduling")
        
        # Filter nodes with sufficient resources
        suitable_nodes = [node for node in available_nodes if node.available_cores >= cpu_required]
        
        if not suitable_nodes:
            logger.warning(f"No node has sufficient resources ({cpu_required} CPU cores)")
            raise Exception(f"No node has sufficient resources ({cpu_required} CPU cores)")
        
        # Select node based on scheduling algorithm
        selected_node = None
        
        if self.scheduling_algorithm == "first-fit":
            # First-Fit: Select the first node that can accommodate the pod
            selected_node = suitable_nodes[0]
        
        elif self.scheduling_algorithm == "best-fit":
            # Best-Fit: Select the node with the least remaining resources that can still fit the pod
            selected_node = min(suitable_nodes, key=lambda node: node.available_cores - cpu_required)
        
        elif self.scheduling_algorithm == "worst-fit":
            # Worst-Fit: Select the node with the most remaining resources
            selected_node = max(suitable_nodes, key=lambda node: node.available_cores)
        
        # Add pod to selected node
        success = self.node_manager.add_pod_to_node(selected_node.id, pod_id, cpu_required)
        
        if success:
            logger.info(f"Scheduled pod {pod_id} on node {selected_node.id}")
            return {
                "pod_id": pod_id,
                "node_id": selected_node.id,
                "cpu_allocated": cpu_required
            }
        else:
            logger.error(f"Failed to schedule pod {pod_id}")
            raise Exception("Failed to schedule pod")
    
    def reschedule_pod(self, pod):
        """
        Reschedule a failed pod on another node
        
        Args:
            pod (Pod): The pod to reschedule
            
        Returns:
            dict: Dictionary containing pod_id and new_node_id if rescheduled successfully
            None: If rescheduling failed
        """
        try:
            logger.info(f"Attempting to reschedule pod {pod.id}")
            
            # Try to schedule a new pod with the same resource requirements
            result = self.schedule_pod(pod.cpu_required)
            
            if result:
                # Mark the old pod as REPLACED
                pod.status = "REPLACED"
                logger.info(f"Pod {pod.id} rescheduled as {result['pod_id']} on node {result['node_id']}")
                
                return {
                    "original_pod_id": pod.id,
                    "new_pod_id": result["pod_id"],
                    "new_node_id": result["node_id"]
                }
            
            return None
        except Exception as e:
            logger.error(f"Failed to reschedule pod {pod.id}: {str(e)}")
            return None