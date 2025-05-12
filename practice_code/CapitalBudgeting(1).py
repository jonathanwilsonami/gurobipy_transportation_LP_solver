import gurobipy as gp

B = 14
sizes = [5, 7, 4, 3]
rewards = [16, 22, 12, 8]
n = len(sizes)

m = gp.Model()
m.modelSense = gp.GRB.MAXIMIZE

x = {}
for i in range(n):
    x[i] = m.addVar(lb = 0, ub = 1, vtype = gp.GRB.INTEGER)
    
m.addConstr(sum(sizes[i]*x[i] for i in range(n)) <= B)
m.setObjective(sum(rewards[i]*x[i] for i in range(n)))
m.optimize()

for i in range(n):
    print(f"x[{i}] = {x[i].x}")

print(f"obj val = {m.ObjVal}")

for i in range(n):
    print(i, rewards[i]/sizes[i])
