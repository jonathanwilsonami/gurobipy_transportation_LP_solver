# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 18:50:54 2023

@author: Hadi
"""

import gurobipy as gp

m = gp.Model()

x = {}

activities = ['A', 'B', 'C', 'D', 'E', 'F', 'dummy']


for i in range(1,7):
    x[i] = m.addVar(lb = 0, name = f"x{i}")
   
    
c = {}

c["A"] = m.addConstr(x[3] >= x[1] + 6)
c["B"] = m.addConstr(x[2] >= x[1] + 9)

c["dummy"] = m.addConstr(x[3] >= x[2])

c["C"] = m.addConstr(x[5] >= x[3] + 8)
c["D"] = m.addConstr(x[4] >= x[3] + 7)

c["E"] = m.addConstr(x[5] >= x[4] + 10)

c['F'] = m.addConstr(x[6] >= x[5] + 12)


m.setObjective(x[6] - x[1])
m.update()

m.optimize()

for i in range(1,7):
    print(f"x{i} = {x[i].x}")
    
for a in activities:
    print(f"SP{a} = {c[a].Pi}")