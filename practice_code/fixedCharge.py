import gurobipy as gp


M = 9999999

PRICE = [12, 8, 15]
VARCOST = [6, 4, 8]
FIXEDCOST = [200, 150, 100]

LABORCAP = 150
CLOTHCAP = 160
LABOR = [3, 2, 6]
CLOTH = [4, 3, 4]

n = len(PRICE)

m = gp.Model()
m.modelSense = gp.GRB.MAXIMIZE

x = {}
y = {}
for i in range(n):
    x[i] = m.addVar(lb = 0, vtype = gp.GRB.INTEGER, name = f"x[{i}]")
    y[i] = m.addVar(vtype = gp.GRB.BINARY, name = f"y[{i}]")


for i in range(n):
    m.addConstr(x[i] <= M*y[i])

m.addConstr(sum(LABOR[i]*x[i] for i in range(n)) <= LABORCAP)
m.addConstr(sum(CLOTH[i]*x[i] for i in range(n)) <= CLOTHCAP)

    
m.setObjective(sum((PRICE[i]-VARCOST[i]) * x[i] for i in range(n)) - sum(FIXEDCOST[i] * y[i] for i in range(n))  )
m.optimize()

for i in range(n):
    print(f"x[{i}] = {x[i].x}")

for i in range(n):
    print(f"y[{i}] = {y[i].x}")

print(f"obj val = {m.ObjVal}")
m.write("fixedCharge.lp")
