#!/usr/bin/python

from gurobipy import *



#This is a function that read in a text file of numbers
#and creates a list of lists in which each list has the
#numbers in one line. The list will have m elements
# m is the number of lines
#each sub list has n numbers and n is number of columns
# or the number of elements in each line
def Read_txt_to_list(FileName):
    with open(FileName) as f:
        Data = []
        for line in f:
            line = line.split() # to deal with blank 
            if line:            # lines (ie skip them)
                line = [int(i) for i in line]
                Data.append(line)
    print(Data)
    return Data


#Calling the function and passing the name of file
#and assigning it to a list named TransCost
TransCost = Read_txt_to_list('TransCost.txt')

#TransCost = [[20, 11, 3, 6],
            #[5, 9, 10, 2],
#             [18, 7, 4, 1]]


Demand = [3, 3, 12, 12]
Supply = [5, 10, 15]

SupplyNode = len(Supply)
DemandNode = len(Demand)

m = Model()
m.modelSense = GRB.MINIMIZE

x = {}
for i in range(SupplyNode):
    for j in range(DemandNode):
        x[i, j] = m.addVar(lb = 0, vtype = GRB.CONTINUOUS)

m.update()

m.setObjective(quicksum(quicksum(TransCost[i][j] * x[i, j] for j in range(DemandNode)) for i in range(SupplyNode)))

SupConst = {}
for i in range(SupplyNode):
    SupConst[i] = m.addConstr(quicksum(x[i, j] for j in range(DemandNode)) == Supply[i])

m.update()

DemConst = {}
for j in range(DemandNode):
    m.addConstr(quicksum(x[i, j] for i in range(SupplyNode)) == Demand[j])

m.update()

m.optimize()

print("Optimal Transportation Cost = ", m.objVal)

print("Transportation Amounts: ")

for i in range(SupplyNode):
    for j in range(DemandNode):
        if j < DemandNode - 1:
            print(x[i, j].x,)
        else:
            print(x[i, j].x)

