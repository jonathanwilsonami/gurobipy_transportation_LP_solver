import gurobipy as gp

e = -1

nodes = list(range(6))

d = [[e, 6, 5, e, e, e],[e, e, e, 3, 1, e],[e,e,e,4,e,e],[e,e,e,e,e,1],[e,e,e,1,e,4]]



m = gp.Model()

x = {}
for i in nodes[0:-1]:
    for j in nodes:
        if d[i][j] != e:
            x[i,j] = m.addVar(lb = 0, name = f"x{i}{j}")
         
# print(x)         
c = {}
c[0] = m.addConstr(sum(x[0,j] for j in nodes if d[0][j] != e) == 1)

c[5] = m.addConstr(sum(x[i,5] for i in nodes[0:-1] if d[i][5] != e) == 1)

for k in nodes[1:-1]:
    c[k] = m.addConstr(sum(x[i,k] for i in nodes[0:-1] if d[i][k] != e) == sum(x[k,j] for j in nodes if d[k][j] != e))
   
m.update()
m.setObjective(sum(x[k]*d[k[0]][k[1]] for k in x.keys() ))
m.modelSense = gp.GRB.MINIMIZE


m.write("SP.lp")
m.optimize()

for k in x.keys():
    print(f"x{k} = {x[k].x}")
    
print(f"obj val = {m.ObjVal}")
