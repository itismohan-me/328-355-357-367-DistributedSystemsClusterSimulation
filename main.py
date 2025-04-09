import logging
import threading
from api_server.app import app
from api_server.node_manager import NodeManager
from api_server.pod_scheduler import PodScheduler
from api_server.health_monitor import HealthMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize and start the Kubernetes-like simulation system"""
    logger.info("Starting Distributed Systems Cluster Simulation")
    
    # Initialize components
    node_manager = NodeManager()
    pod_scheduler = PodScheduler(node_manager)
    health_monitor = HealthMonitor(node_manager)
    
    # Connect components
    health_monitor.set_pod_scheduler(pod_scheduler)
    
    # Set scheduling algorithm
    pod_scheduler.set_scheduling_algorithm("best-fit")  # Can be 'first-fit', 'best-fit', or 'worst-fit'
    
    # Start health monitoring in a separate thread
    monitoring_thread = threading.Thread(target=health_monitor.start_monitoring, daemon=True)
    monitoring_thread.start()
    
    # Start the API server
    logger.info("Starting API server")
    app.run(host='0.0.0.0', port=5050)

if __name__ == "__main__":
    main()