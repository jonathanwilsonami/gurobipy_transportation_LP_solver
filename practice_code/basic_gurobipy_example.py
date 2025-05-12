import gurobipy as gp

#build a model m
m = gp.Model("class example")

#tell gurobi that you want to maximize
m.modelSense = gp.GRB.MAXIMIZE # m.modelSense = gp.GRB.MAXIMIZE

#Declare variables and add them to model m
x1 = m.addVar(lb = 0, vtype = gp.GRB.CONTINUOUS, name = 'x1')
x2 = m.addVar(lb = 0, vtype = gp.GRB.CONTINUOUS, name = 'x2')
#after definitions in gurobi, m.update() is needed 
m.update()

#define the objective function
m.setObjective(3*x1 + 2*x2) # m.setObjective(3*x1 + 2*x2)
m.update()

#define constraints and add them to model m
c1 = m.addConstr(2*x1 + x2 <= 101) # c1 = m.addConstr(2*x1 + x2 <= 100)
c2 = m.addConstr(x1 + x2 <= 80)
c3 = m.addConstr(x1 <= 40)
m.update()

#solve the model
m.optimize()

print ('Objective = ', m.objVal)
print ('x1 = ', x1.x)
print ('x2 = ', x2.x)

print ('Constraint 1 Slack = ', c1.Slack)
print ('Constraint 2 Slack = ', c2.Slack)
print ('Constraint 3 Slack = ', c3.Slack)

print ('Constraint 1 Shadow Price = ', c1.Pi)
print ('Constraint 2 Shadow Price = ', c2.Pi)
print ('Constraint 3 Shadow Price = ', c3.Pi)

print ('x1 sensitivity: ', x1.SAObjLow, " - ", x1.SAObjUp)
print ('x2 sensitivity: ', x2.SAObjLow, " - ", x2.SAObjUp)

print ('RHS 1 range :', c1.SARHSLow, " - ", c1.SARHSUp)
print ('RHS 2 range :', c2.SARHSLow, " - ", c2.SARHSUp)
print ('RHS 3 range :', c3.SARHSLow, " - ", c3.SARHSUp)

m.write("model.lp")
m.write("model.sol")
