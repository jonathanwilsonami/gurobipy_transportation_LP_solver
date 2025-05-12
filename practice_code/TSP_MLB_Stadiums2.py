#!/usr/bin/python

import gurobipy as gp



#This is a function that read in a text file of numbers
#and creates a list of lists in which each list has the
#numbers in one line. The list will have m elements
# m is the number of lines
#each sub list has n numbers and n is number of columns
# or the number of elements in each line
# def Read_txt_to_list(FileName):
#     with open(FileName) as f:
#         Data = []
#         for line in f:
#             line = line.split() # to deal with blank 
#             if line:            # lines (ie skip them)
#                 line = [int(i) for i in line]
#                 Data.append(line)

#     return Data



Location = ['Fairfax', 'Fenway', 'Wrigley', 'Dodger', 'Kauffman', 'Rogers']

m = 10000000
Distance = [[m, 455, 706, 2654, 1052, 480],
            [455, m, 986, 2983, 1408, 546],
            [706, 986, m, 2020, 517, 525],
            [2654, 2983, 2020, m, 1625, 2519],
            [1052, 1408, 517, 1625, m, 1001],
            [480, 546, 525, 2519, 1001, m]]

N = len(Location)

m = gp.Model()
m.modelSense = gp.GRB.MINIMIZE

x = {}
for i in range(N):
    for j in range(N):
        x[i, j] = m.addVar(vtype = gp.GRB.BINARY, name = f"x[{Location[i]},{Location[j]}]")

y = {}
for i in range(N):
    y[i] = m.addVar(lb = 0, vtype = gp.GRB.CONTINUOUS, name = f"y[{i}]")

m.update()

m.setObjective(sum(Distance[i][j] * x[i, j] for j in range(N) for i in range(N)))

m.update()

ToCons = {}
for i in range(N):
    ToCons[i] = m.addConstr(sum(x[i, j] for j in range(N)) == 1)
m.update()

FromCons = {}
for j in range(len(Location)):
    FromCons[j] = m.addConstr(sum(x[i, j] for i in range(N)) == 1)
m.update()

#subtour constraint for Ffx and Fenway

#m.addConstr(x[0, 1] + x[1, 0] <= 1)
#m.addConstr(x[1, 0] + x[0, 2] + x[2, 5] + x[5, 1] <= 3)
#m.addConstr(x[0, 1] + x[2, 0] + x[5, 2] + x[1, 5] <= 3)
#m.update()


AllSub = {}
for i in range(1, N):
    for j in range(1, N):
        if i!=j:
            AllSub[i, j] = m.addConstr(y[i] - y[j] + (N * x[i, j]) <= N-1)
m.update()


m.optimize()

print ("Optimal Transportation Cost = ", m.objVal)


print ("Planned Trip")

for i in range(N):
    for j in range(N):
        if x[i, j].x >= 0.0001:
            print (Location[i], "--->", Location[j])


       
m.write("TSP_final.lp")
