import os
import time
import requests
import logging
import random
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeAgent:
    def __init__(self):
        self.node_id = os.environ.get('NODE_ID')
        self.cpu_cores = int(os.environ.get('CPU_CORES', 1))
        self.api_server = os.environ.get('API_SERVER', 'http://localhost:5000')
        self.heartbeat_interval = int(os.environ.get('HEARTBEAT_INTERVAL', 5))  # seconds
        
        if not self.node_id:
            raise ValueError("NODE_ID environment variable must be set")
        
        logger.info(f"Node agent started with ID: {self.node_id}, CPU cores: {self.cpu_cores}")
    
    def send_heartbeat(self):
        """Send heartbeat to the API server"""
        try:
            endpoint = f"{self.api_server}/api/nodes/{self.node_id}/heartbeat"
            response = requests.post(endpoint)
            
            if response.status_code == 200:
                logger.debug(f"Heartbeat sent successfully: {response.json()}")
                return True
            else:
                logger.warning(f"Failed to send heartbeat: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending heartbeat: {str(e)}")
            return False
    
    def run(self):
        """Run the node agent continuously sending heartbeats"""
        while True:
            self.send_heartbeat()
            
            # Simulate occasional random failures (for testing)
            if random.random() < 0.01:  # 1% chance of failing to send a heartbeat
                logger.warning("Simulating node failure by skipping heartbeat")
                time.sleep(self.heartbeat_interval * 3)  # Sleep longer to simulate failure
            
            time.sleep(self.heartbeat_interval)

if __name__ == '__main__':
    node_agent = NodeAgent()
    node_agent.run()