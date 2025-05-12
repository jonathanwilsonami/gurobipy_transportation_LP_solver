import gurobipy as gp

B = 50
sizes = [7, 3, 19, 8, 11, 13, 29, 17, 19, 31, 23, 5]
rewards = [1, 2, 5, 4, 3, 7, 9, 6, 8, 10, 11, 3]
n = len(sizes)

m = gp.Model()
m.modelSense = gp.GRB.MAXIMIZE

x = {}
for i in range(n):
    x[i] = m.addVar(lb = 0, ub = 1, vtype = gp.GRB.BINARY)
    
m.addConstr(sum(sizes[i]*x[i] for i in range(n)) <= B)
m.setObjective(sum(rewards[i]*x[i] for i in range(n)))
m.optimize()

for i in range(n):
    print(f"x[{i}] = {x[i].x}")

print(f"obj val = {m.ObjVal}")

for i in range(n):
    print(i, rewards[i]/sizes[i])
