import gurobipy as gp


M = [2000, 2000, 1200]
PROFIT = [2, 3, 4]
STEEL = [1.5, 3, 5]
LABOR = [30, 25, 40]

STEELCAP = 6000
LABORCAP = 60000

MINREQ = [1000, 1000, 1000]

n = len(PROFIT)

m = gp.Model()
m.modelSense = gp.GRB.MAXIMIZE

x = {}
y = {}
for i in range(n):
    x[i] = m.addVar(lb = 0, vtype = gp.GRB.INTEGER, name = f"x[{i}]")
    y[i] = m.addVar(vtype = gp.GRB.BINARY, name = f"y[{i}]")


for i in range(n):
    m.addConstr(MINREQ[i] - x[i] <= M[i]*y[i])
    m.addConstr(x[i] <= M[i]*(1-y[i]))

m.addConstr(sum(STEEL[i]*x[i] for i in range(n)) <= STEELCAP)
m.addConstr(sum(LABOR[i]*x[i] for i in range(n)) <= LABORCAP)

# If midsize are produced then compacts must be produced
y[3] = m.addVar(vtype = gp.GRB.BINARY, name = "y[3]")
m.addConstr(x[1] <= 9999 * y[3])
m.addConstr(1-x[0] <= 9999 * (1-y[3]))


# Either Compacts or midsize need to be produced (or both)
# y[3] = m.addVar(vtype = gp.GRB.BINARY, name = "y[3]")
# m.addConstr(1 - x[0] <= 9999 * y[3])
# m.addConstr(1 - x[2] <= 9999 * (1-y[3]))

    
m.setObjective(sum(PROFIT[i] * x[i] for i in range(n)) )
m.optimize()

for i in range(n):
    print(f"x[{i}] = {x[i].x}")

for i in range(n):
    print(f"y[{i}] = {y[i].x}")

print(f"obj val = {m.ObjVal}")
m.write("EitherOR.lp")
