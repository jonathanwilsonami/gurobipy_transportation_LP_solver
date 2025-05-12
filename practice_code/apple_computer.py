#Apple computer example from class
import gurobipy as gp


#Problem data
Vendor = 2
Quarters = 4
Demand = {1:35 , 2:50, 3:30, 4:60}
RegCost = 200
OutCost = 230
HoldCost = 50
SalvageVal = 150
InitialInv = 10
RegCap = 30
OutCap = 20

#Build gurobi model m
m = gp.Model()

#sense of the objective function
m.modelSense = gp.GRB.MINIMIZE

#Declare variables and add them to model m

#regular production variables
x = {}
for q in range(1, Quarters + 1):
    x[q] = m.addVar(lb = 0, vtype = gp.GRB.CONTINUOUS, name = "x"+str(q))
    #x[q] = m.addVar(lb = 0, ub = RegCap, vtype = GRB.COMTINUOUS)

# m.update()

#outsourcing variables
y = {}
for v in range(1, Vendor + 1):
    for q in range(1, Quarters + 1):
        y[v, q] = m.addVar(lb = 0, vtype = gp.GRB.CONTINUOUS, name = "y["+str(v)+","+str(q)+"]")
        #y[v, q] = m.addVar(lb = 0, ub = OutCap, vtype = GRB.CONTINUOUS)
# m.update()

#inventory variables
I ={}
for q in range(Quarters + 1):
    I[q] = m.addVar(lb = 0, vtype = gp.GRB.CONTINUOUS, name = "I"+str(q))
# m.update()


#define the objective function
m.setObjective(RegCost * sum(x[q] for q in range(1, Quarters + 1)) +
               OutCost *sum( (y[1, q] + y[2, q]) for q in range(1, Quarters + 1)) +
               HoldCost * sum(I[q] for q in range(1, Quarters))
               - (SalvageVal * I[Quarters]))
# m.update()

#define constrainst and add them to model m
#Define the initial constraint for initial inventory
m.addConstr(I[0] == InitialInv)
# m.update()

#Define the inventory evolution
InvCons = {}
for q in range(1, Quarters + 1):
    InvCons[q] = m.addConstr(I[q] == I[q-1] + x[q] + y[1, q] + y[2, q] - Demand[q])
               
# m.update()

#constraints for regular capacity
CapConsReg = {}
for q in range(1, Quarters + 1):
    CapConsReg[q] = m.addConstr(x[q] <= RegCap)

# m.update()

#constraints for vendor capacity
CapConsVendor = {}
for v in range(1, Vendor + 1):
    for q in range(1, Quarters + 1):
        CapConsVendor[v, q] = m.addConstr(y[v, q] <= OutCap)

m.update()

m.optimize()

#This will write out a .lp file named Apple.lp
m.write("Apple2.lp")

