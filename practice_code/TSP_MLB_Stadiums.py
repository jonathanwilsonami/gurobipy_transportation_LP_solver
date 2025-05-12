#!/usr/bin/python

import gurobipy as gp



Location = ['Fairfax', 'Fenway', 'Wrigley', 'Dodger', 'Kauffman', 'Rogers']
N = len(Location)
m = 1000000
Distance = [[m, 455, 706, 2654, 1052, 480],
            [455, m, 986, 2983, 1408, 546],
            [706, 986, m, 2020, 517, 525],
            [2654, 2983, 2020, m, 1625, 2519],
            [1052, 1408, 517, 1625, m, 1001],
            [480, 546, 525, 2519, 1001, m]]

m = gp.Model()
m.modelSense = gp.GRB.MINIMIZE

x = {}

for i in range(N):
    for j in range(N):
        x[i, j] = m.addVar(vtype = gp.GRB.BINARY, name = f"x[{Location[i]},{Location[j]}])")

m.update()

m.setObjective(sum(Distance[i][j] * x[i, j] for j in range(N) for i in range(N)))

m.update()

ToCons = {}
for i in range(N):
    ToCons[i] = m.addConstr(sum(x[i, j] for j in range(N)) == 1)
m.update()

FromCons = {}
for j in range(N):
    FromCons[j] = m.addConstr(sum(x[i, j] for i in range(N)) == 1)
m.update()


m.optimize()

print ("Optimal Transportation Cost = ", m.objVal)


print ("\nPlanned Trip:\n")

for i in range(N):
    for j in range(N):
        if x[i, j].x >= .0001:
            print (Location[i], "--->", Location[j])


       

