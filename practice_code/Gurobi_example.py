from gurobipy import Model, GRB

# Parameters
demand = [35000, 50000, 30000, 60000]  # Demand in each quarter
inventory_cost = 50  # Cost per phone in inventory
regular_cost = 200  # Cost per phone for regular production
overtime_cost = 250  # Cost per phone for overtime production
max_production = 40000  # Max phones produced per quarter
initial_inventory = 10000  # Initial inventory

# Create the model
model = Model("Minimize_Production_Costs")

# Decision variables
R = model.addVars(4, lb=0, name="R")  # Regular production
O = model.addVars(4, lb=0, name="O")  # Overtime production
I = model.addVars(4, lb=0, name="I")  # Inventory at end of each quarter

# Objective function
model.setObjective(
    sum(regular_cost * R[t] + overtime_cost * O[t] + inventory_cost * I[t] for t in range(4)),
    GRB.MINIMIZE
)

# Constraints
# Inventory balance constraints
model.addConstr(R[0] + O[0] + initial_inventory - I[0] == demand[0], name="Balance_Q1")
for t in range(1, 4):
    model.addConstr(R[t] + O[t] + I[t-1] - I[t] == demand[t], name=f"Balance_Q{t+1}")

# Production capacity constraints
for t in range(4):
    model.addConstr(R[t] + O[t] <= max_production, name=f"Capacity_Q{t+1}")

# Optimize the model
model.optimize()

# Print results
if model.status == GRB.OPTIMAL:
    print(f"Optimal Costs: {model.objVal}")
    for t in range(4):
        print(f"Q{t+1}: Regular Production = {R[t].x:.0f}, Overtime Production = {O[t].x:.0f}, Inventory = {I[t].x:.0f}")
else:
    print("No optimal solution found.")
