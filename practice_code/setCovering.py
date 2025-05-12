import gurobipy as gp

MAX_DIST = 15

DISTANCES = [[0, 14, 14, 17, 13], 
[14, 0, 24, 14, 21], 
[14, 24, 0, 18, 17], 
[17, 14, 18, 0, 30], 
[13, 21, 17, 30, 0]]

n = len(DISTANCES)

m = gp.Model()
m.modelSense = gp.GRB.MINIMIZE

x = {}
for i in range(n):
    x[i] = m.addVar(vtype = gp.GRB.BINARY, name = f"x[{i}]")

for i in range(n):
    m.addConstr(sum(x[j] for j in range(n) if DISTANCES[i][j] <= MAX_DIST) >= 1)

    
m.setObjective(sum(x[i] for i in range(n)))
m.optimize()

for i in range(n):
    print(f"x[{i}] = {x[i].x}")

print(f"obj val = {m.ObjVal}")
m.write("SetCovering.lp")
