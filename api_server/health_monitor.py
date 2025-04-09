import threading
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self, node_manager, pod_scheduler=None):
        self.node_manager = node_manager
        self.pod_scheduler = pod_scheduler
        self.heartbeat_timeout = 60  # seconds before a node is considered failed
        self.check_interval = 5  # seconds between health checks
        self.running = False
    
    def set_pod_scheduler(self, pod_scheduler):
        """Set the pod scheduler reference for rescheduling pods"""
        self.pod_scheduler = pod_scheduler
    
    def process_heartbeat(self, node_id):
        """
        Process a heartbeat from a node
        
        Args:
            node_id (str): ID of the node sending the heartbeat
        """
        self.node_manager.update_node_heartbeat(node_id)
    
    def check_node_health(self):
        """Check the health of all nodes and handle failures"""
        current_time = time.time()
        
        for node_id, node in list(self.node_manager.nodes.items()):
            # Skip nodes that are already marked as failed
            if node.status == "FAILED":
                continue
            
            # Check if node has timed out
            if current_time - node.last_heartbeat > self.heartbeat_timeout:
                logger.warning(f"Node {node_id} failed to send heartbeat for {self.heartbeat_timeout} seconds")
                
                # Mark node as failed and get its pods
                failed_pods_ids = self.node_manager.handle_node_failure(node_id)
                
                # Attempt to reschedule pods if a pod scheduler is available
                if self.pod_scheduler and failed_pods_ids:
                    self.reschedule_failed_pods(failed_pods_ids)
    
    def reschedule_failed_pods(self, pod_ids):
        """
        Reschedule pods from a failed node
        
        Args:
            pod_ids (list): List of pod IDs to reschedule
        """
        if not self.pod_scheduler:
            logger.warning("Cannot reschedule pods: Pod scheduler not available")
            return
        
        logger.info(f"Attempting to reschedule {len(pod_ids)} pods")
        
        for pod_id in pod_ids:
            pod = self.node_manager.get_pod(pod_id)
            if pod and pod.status == "FAILED":
                result = self.pod_scheduler.reschedule_pod(pod)
                if result:
                    logger.info(f"Pod {pod_id} rescheduled successfully")
                else:
                    logger.warning(f"Failed to reschedule pod {pod_id}")
    
    def start_monitoring(self):
        """Start the health monitoring loop"""
        self.running = True
        logger.info("Health monitoring started")
        
        while self.running:
            try:
                self.check_node_health()
            except Exception as e:
                logger.error(f"Error in health monitoring: {str(e)}")
            
            time.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop the health monitoring loop"""
        self.running = False
        logger.info("Health monitoring stopped")