import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Load the dataset
file_path = 'port_data.csv'
port_data = pd.read_csv(file_path)

# Extract relevant data
vessels = port_data['Port Name'].unique()
berths = ['Berth1', 'Berth2', 'Berth3']  # Assuming three berths for simplicity
cranes = ['Crane1', 'Crane2', 'Crane3', 'Crane4', 'Crane5']  # Assuming five cranes

# Generate synthetic arrival and handling times
import numpy as np

np.random.seed(0)
arrival = {v: np.random.randint(0, 10) for v in vessels}
handling = {v: np.random.randint(5, 20) for v in vessels}

# Berth capacities (max number of cranes per berth)
berth_capacity = {b: 2 for b in berths}  # Assuming a maximum of 2 cranes per berth

# Create a new model
m = gp.Model("container_terminal")

# Variables
x = m.addVars(vessels, berths, cranes, vtype=GRB.BINARY, name="assign")
start = m.addVars(vessels, berths, vtype=GRB.CONTINUOUS, name="start")

# Objective: Minimize total makespan (max completion time of all vessels)
m.setObjective(gp.quicksum(start[v,b] + handling[v] * x[v,b,c] for v in vessels for b in berths for c in cranes), GRB.MINIMIZE)

# Constraints
# Each vessel is assigned to exactly one berth and one crane
for v in vessels:
    m.addConstr(gp.quicksum(x[v,b,c] for b in berths for c in cranes) == 1)

# Crane capacity at each berth
for b in berths:
    m.addConstr(gp.quicksum(x[v,b,c] for v in vessels for c in cranes) <= berth_capacity[b])

# No overlap constraint
M = 1000  # A large constant for the no overlap constraint
for v in vessels:
    for b in berths:
        m.addConstr(start[v,b] >= arrival[v])
        for v2 in vessels:
            if v != v2:
                for c in cranes:
                    m.addConstr(start[v,b] >= start[v2,b] + handling[v2] * x[v2,b,c] - (1 - x[v,b,c]) * M)

# Optimize model
m.optimize()

# Print solution
solution = []
for v in vessels:
    for b in berths:
        for c in cranes:
            if x[v,b,c].x > 0.5:
                solution.append({
                    'Vessel': v,
                    'Berth': b,
                    'Crane': c,
                    'Start Time': start[v,b].x
                })

# Convert solution to a DataFrame and display
solution_df = pd.DataFrame(solution)
solution_df
