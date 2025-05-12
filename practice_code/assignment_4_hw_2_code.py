from gurobipy import *
import pandas as pd
from pathlib import Path
import os

def read_data(file_name):
    script_dir = Path(__file__).parent.resolve()
    file_path = (script_dir / file_name).resolve()

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_name.endswith('.xlsx'):
        df = pd.read_excel(file_name, engine='openpyxl')
    elif file_name.endswith('.ods'):
        df = pd.read_excel(file_name, engine='odf')
    else:
        raise ValueError("Unsupported file format. Use .xlsx or .ods")

    supply = df.drop_duplicates('P')['Supply'].tolist()          
    demand = df.loc[df['P'] == df.iloc[0]['P'], 'Demand'].tolist()

    # Create trans_cost matrix grouped by supply
    trans_cost = []
    for s in supply:
        costs = df[df['Supply'] == s]['Shipping_Cost'].astype(int).tolist()
        trans_cost.append(costs)

    return supply, demand, trans_cost

supply, demand, trans_cost = read_data('/home/jon/Documents/grad_school/OR/code/hw/data/a4_transportation.ods')
print(supply, demand, trans_cost)

supply_node = len(supply)
demand_node = len(demand)

m = Model()
m.modelSense = GRB.MINIMIZE

x = {}
for i in range(supply_node):
    for j in range(demand_node):
        x[i, j] = m.addVar(lb = 0, vtype = GRB.CONTINUOUS, name=f"x_{i+1}_{j+1}")

m.setObjective(quicksum(quicksum(trans_cost[i][j] * x[i, j] for j in range(demand_node)) for i in range(supply_node)))

SupConst = {}
for i in range(supply_node):
    SupConst[i] = m.addConstr(quicksum(x[i, j] for j in range(demand_node)) == supply[i], name=f"supply_{i+1}")

DemConst = {}
for j in range(demand_node):
    m.addConstr(quicksum(x[i, j] for i in range(supply_node)) == demand[j], name=f"demand_{j+1}")

m.update()
m.optimize()

print("Optimal Transportation Cost = ", m.objVal)

print("Transportation Amounts: ")

for i in range(supply_node):
    for j in range(demand_node):
        if j < demand_node - 1:
            print(x[i, j].x,)
        else:
            print(x[i, j].x)

m.write("model_hw4_2.lp")
m.write("model_hw4_2.sol")

