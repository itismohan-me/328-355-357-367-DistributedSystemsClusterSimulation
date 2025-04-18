# Distributed Systems Cluster Simulation Framework 

A lightweight simulation-based distributed system that mimics core Kubernetes cluster management functionalities, providing a simplified yet comprehensive platform for demonstrating key distributed computing concepts.

## Project Overview

This framework simulates a Kubernetes-like system with the following components:

- **API Server**: Central control unit that manages the overall cluster operation
- **Node Manager**: Tracks registered nodes and their statuses
- **Pod Scheduler**: Assigns pods to available nodes based on scheduling policies
- **Health Monitor**: Receives health signals from nodes and handles failures

## Architecture

The system consists of:

1. **API Server**: Flask-based REST API that exposes endpoints for node and pod management
2. **Node Containers**: Docker containers that simulate physical nodes in the cluster
3. **CLI**: Command-line interface for user interaction with the cluster

## Features

- **Node Management**: Add nodes to the cluster with specified CPU resources
- **Pod Scheduling**: Schedule pods with specific CPU requirements using various algorithms (First-Fit, Best-Fit, Worst-Fit)
- **Health Monitoring**: Detect node failures through heartbeat mechanisms
- **Fault Tolerance**: Automatically reschedule pods from failed nodes to healthy ones


## Getting Started

### Prerequisites

- Python 3.9+
- Docker
- Git


## API Endpoints

### Node Management
- `GET /api/nodes`: List all nodes and their status
- `POST /api/nodes`: Add a new node to the cluster
  - Request body: `{"cpu_cores": <int>}`
- `POST /api/nodes/<node_id>/heartbeat`: Receive heartbeat from a node

### Pod Management
- `POST /api/pods`: Launch a new pod
  - Request body: `{"cpu_required": <int>}`

## Scheduling Algorithms

The system supports three scheduling algorithms:

1. **First-Fit**: Assigns pods to the first node that has sufficient resources
2. **Best-Fit**: Assigns pods to nodes with the least remaining resources that can still fit the pod
3. **Worst-Fit**: Assigns pods to nodes with the most remaining resources

To change the scheduling algorithm, modify the `pod_scheduler.set_scheduling_algorithm()` call in `main.py`.

## Health Monitoring and Fault Tolerance

The system automatically monitors node health by expecting periodic heartbeats. If a node fails to send heartbeats, it's marked as failed, and the system attempts to reschedule its pods to other healthy nodes.

## Testing

Run the tests using pytest:
```
pytest
```

## Implementation Details

### Node Manager
The Node Manager tracks all nodes in the cluster and maintains information about their resources and status. It's responsible for:
- Adding new nodes to the cluster
- Tracking node health status
- Managing pod assignments to nodes

### Pod Scheduler
The Pod Scheduler is responsible for deciding which node should host a pod based on the pod's resource requirements and the chosen scheduling algorithm.

### Health Monitor
The Health Monitor periodically checks node health by monitoring heartbeats. When a node fails to send heartbeats within the timeout period, it's marked as failed, and recovery actions are triggered.

## Weekly Progress

### Week 1
- Implemented API Server base and Node Manager functionality
- Added functionality to add nodes to the cluster
- Set up Docker infrastructure for node simulation

### Week 2
- Implemented Pod Scheduler with multiple scheduling algorithms
- Added Health Monitor with node heartbeat mechanism
- Implemented pod launching functionality

### Week 3
- Added node listing functionality
- Implemented system testing
- Completed documentation

## Extensions and Enhancements

Potential extensions to the project:
- Web-based UI for cluster management
- Node auto-scaling based on cluster load
- Pod resource usage monitoring
- Network policy simulation for pod communication control

## Contributors
- [MANAS R] ([PES1UG22CS328])
- [MOHAMMED KAIF] ([PES1UG22CS355])
- [MOHAN E] ([PES1UG22CS357])
- [N PRANAV KUMAR] ([PES1UG22CS367])

## License
This project is licensed under the MIT License - see the LICENSE file for details.
