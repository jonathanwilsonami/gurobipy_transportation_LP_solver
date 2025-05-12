import gurobipy as gp

I = [1, 2, 3, 4, 5, 6]

m = gp.Model()
m.modelSense = gp.GRB.MINIMIZE

x = m.addVars(I, lb = 0, ub = 8, vtype = gp.GRB.INTEGER)

m.addConstr(x[1]+x[6] >= 3)
m.addConstr(x[1]+x[2] >= 2)
m.addConstr(x[2]+x[3] >= 10)
m.addConstr(x[3]+x[4] >= 6)
m.addConstr(x[4]+x[5] >= 8)
m.addConstr(x[5]+x[6] >= 5)

m.setObjective(sum(x[i] for i in I))

m.optimize()

for i in I:
    print(f'x{i} = {x[i].x}')
    
print(f'Objective = {m.ObjVal}')
