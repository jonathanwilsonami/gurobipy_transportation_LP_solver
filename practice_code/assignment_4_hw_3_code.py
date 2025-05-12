from pathlib import Path
import pandas as pd
from gurobipy import Model, GRB, quicksum

def read_data(file_name):
    file_path = Path(file_name).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix == '.xlsx':
        df = pd.read_excel(file_path, engine='openpyxl')
    elif file_path.suffix == '.ods':
        df = pd.read_excel(file_path, engine='odf')
    else:
        raise ValueError("Unsupported file format. Use .xlsx or .ods")

    grouped = df.groupby(["P", "Job"], as_index=False)["Time"].min()

    employees = grouped["P"].unique().tolist()
    jobs = grouped["Job"].unique().tolist()

    trans_cost = []
    for e in employees:
        costs = df[df['P'] == e]['Time'].astype(int).tolist()
        trans_cost.append(costs)
        
    return employees, jobs, trans_cost

def build_assignment_model(employees, jobs, cost):
    employee_node = len(employees)
    job_node = len(jobs)
    m = Model("Assignment")
    m.modelSense = GRB.MINIMIZE

    x = {}
    for i in range(employee_node):
        for j in range(job_node):
            x[i, j] = m.addVar(vtype=GRB.BINARY, name=f"x_{i+1}_{j+1}")
            
    m.setObjective(quicksum(quicksum(cost[i][j] * x[i, j] for j in range(job_node)) for i in range(employee_node)))

    for i in range(employee_node):
        m.addConstr(quicksum(x[i, j] for j in range(job_node)) == 1, name=f"assign_{i+1}")
    for j in range(job_node):
        m.addConstr(quicksum(x[i, j] for i in range(employee_node)) == 1, name=f"job_{j+1}")
    
    m.update()
    return m

def solve_and_display(m):
    m.optimize()   
    m.write("model_hw4_3.lp")
    m.write("model_hw4_3.sol")

def main():
    file_name = "../code/hw/data/a4_arrangement.ods"  
    employees, jobs, cost = read_data(file_name)

    m = build_assignment_model(employees, jobs, cost)
    
    solve_and_display(m)

if __name__ == "__main__":
    main()
