import time

class Node:
    def __init__(self, id, cpu_cores, available_cores, status, last_heartbeat, pods):
        self.id = id
        self.cpu_cores = cpu_cores  # Total CPU cores
        self.available_cores = available_cores  # Available CPU cores
        self.status = status  # HEALTHY, UNHEALTHY, FAILED
        self.last_heartbeat = last_heartbeat  # Timestamp of last heartbeat
        self.pods = pods  # List of pod IDs hosted on this node
    
    def to_dict(self):
        """Convert Node object to dictionary for API responses"""
        return {
            "id": self.id,
            "cpu_cores": self.cpu_cores,
            "available_cores": self.available_cores,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat,
            "pods": self.pods,
            "pod_count": len(self.pods)
        }

class Pod:
    def __init__(self, id, node_id, cpu_required, status):
        self.id = id
        self.node_id = node_id  # ID of the node hosting this pod
        self.cpu_required = cpu_required  # CPU cores required by this pod
        self.status = status  # RUNNING, FAILED
        self.created_at = time.time()  # Timestamp of creation
    
    def to_dict(self):
        """Convert Pod object to dictionary for API responses"""
        return {
            "id": self.id,
            "node_id": self.node_id,
            "cpu_required": self.cpu_required,
            "status": self.status,
            "created_at": self.created_at
        }