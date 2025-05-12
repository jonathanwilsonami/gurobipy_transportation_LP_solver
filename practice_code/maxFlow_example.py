import gurobipy as gp

e = -1

nodes = list(range(5))

cap = [[e, 2, 3, e, e], [e, e, 3, 4, e], [e, e, e, e, 2], [e, e, e, e, 1]]  


m = gp.Model()

x = {}
for i in nodes[0:-1]:
    for j in nodes:
        if cap[i][j] != e:
            x[i,j] = m.addVar(lb = 0, name = f"x{i}{j}")

xf = m.addVar(lb = 0, name = "xf")

# print(x)         
c = {}
c[0] = m.addConstr(sum(x[0,j] for j in nodes if cap[0][j] != e) == xf)

c[4] = m.addConstr(sum(x[i,4] for i in nodes[0:-1] if cap[i][4] != e) == xf)


for k in nodes[1:-1]:
    c[k] = m.addConstr(sum(x[i,k] for i in nodes[0:-1] if cap[i][k] != e) == sum(x[k,j] for j in nodes if cap[k][j] != e))

for k in x.keys():
    print(k[0],k[1])
    c[k] = m.addConstr(x[k] <= cap[k[0]][k[1]])

m.update()
m.setObjective(xf)
m.modelSense = gp.GRB.MAXIMIZE


m.write("maxflow.lp")
m.optimize()

for k in x.keys():
    print(f"x{k} = {x[k].x}")
    
for k in c.keys():
    print(f"pi{k} = {c[k].Pi}")
    
print(f"obj val = {m.ObjVal}")
