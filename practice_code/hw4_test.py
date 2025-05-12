from pathlib import Path
import pandas as pd
from gurobipy import Model, GRB, quicksum


def read_data(file_name):
    script_dir = Path(__file__).parent.resolve()
    file_path = (script_dir / file_name).resolve()

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix == '.xlsx':
        df = pd.read_excel(file_path, engine='openpyxl')
    elif file_path.suffix == '.ods':
        df = pd.read_excel(file_path, engine='odf')
    else:
        raise ValueError("Unsupported file format. Use .xlsx or .ods")
    
    groups = df.groupby("P", sort=False)

    supply = []
    trans_cost = []
    demand = None

    for i, (_, group) in enumerate(groups):
        supply.append(int(group["Supply"].iloc[0]))
        trans_cost.append(group["Shipping_Cost"].astype(int).tolist())
        if i == 0:
            demand = group["Demand"].astype(int).tolist()
    
    return supply, demand, trans_cost


def build_model(supply, demand, trans_cost):
    m = Model("Transportation")
    m.modelSense = GRB.MINIMIZE

    n_suppliers = len(supply)
    n_demands = len(demand)
    x = {}
    
    for i in range(n_suppliers):
        for j in range(n_demands):
            x[i, j] = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name=f"x_{i}_{j}")
    
    m.setObjective(quicksum(trans_cost[i][j] * x[i, j]
                            for i in range(n_suppliers)
                            for j in range(n_demands)))
    
    for i in range(n_suppliers):
        m.addConstr(quicksum(x[i, j] for j in range(n_demands)) == supply[i],
                    name=f"Supply_{i}")
    
    for j in range(n_demands):
        m.addConstr(quicksum(x[i, j] for i in range(n_suppliers)) == demand[j],
                    name=f"Demand_{j}")
    
    m.update()  
    return m, x


def solve_and_display(m, x, supply, demand, solution_name):
    m.optimize()
    
    if m.status == GRB.Status.OPTIMAL:
        print("Optimal Transportation Cost =", m.objVal)
        print("Transportation Amounts:")
        n_suppliers = len(supply)
        n_demands = len(demand)
        for i in range(n_suppliers):
            for j in range(n_demands):
                print(f"x[{i},{j}] = {x[i,j].x:.2f}", end="  ")
            print()
    else:
        print("No optimal solution found; status =", m.status)
    
    m.write(f"model_{solution_name}.lp")
    m.write(f"model_{solution_name}.sol")


def main():
    ######################################################
    ##### #2 #############################
    #####################################
    file_name = "../hw/data/a4_transportation.ods"
    supply, demand, trans_cost = read_data(file_name)

    print("Supply:", supply)
    print("Demand:", demand)
    print("Transportation Cost Matrix:")
    for row in trans_cost:
        print(row)

    m, x = build_model(supply, demand, trans_cost)
    solve_and_display(m, x, supply, demand, "hw4_2")

    ######################################################
    ##### #3 #############################
    #####################################

    file_name = "../hw/data/a4_transportation.ods"
    supply, demand, trans_cost = read_data(file_name)

    print("Supply:", supply)
    print("Demand:", demand)
    print("Transportation Cost Matrix:")
    for row in trans_cost:
        print(row)

    m, x = build_model(supply, demand, trans_cost)
    solve_and_display(m, x, supply, demand, "hw4_3")


if __name__ == "__main__":
    main()
