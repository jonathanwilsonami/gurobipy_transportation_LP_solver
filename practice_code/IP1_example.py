#!/usr/bin/python

import gurobipy as gp
import numpy as np

# N = 5
# loc_x = np.array([1, 3, 5, 7, 8])
# loc_y = np.array([2, 1, 3, 2, 3])

N = 50
loc_x = np.random.randint(0,100,N)
loc_y = np.random.randint(0,100,N)




m = 10000000
Distance = np.zeros([N,N])

for i in range(N):
	Distance[i,i] = m
	for j in range(i+1, N):
		Distance[i,j] = ((loc_x[i]-loc_x[j])**2 + (loc_y[i]-loc_y[j])**2)**0.5
		Distance[j,i] = Distance[i,j]


Distance = Distance.tolist()

for i in range(N):
    Distance[i][i]=m

def findLoops(x):
    loops = []
    # print(x)
    remaining = list(range(N))
    
    while  len(remaining) > 0:
        # print("remaining: ", remaining)
        city = remaining.pop(0)
        tour = [city]
        tourEnd = False
        while not tourEnd:
            tourEnd = True
            # print(tour)
            # print(remaining)
            # print("remaining: ", remaining)
            for dest in remaining:
                # print(city, dest)
                if x[city, dest].x >=.0001:
                    tour.append(dest)
                    # print(tour)
                    remaining.remove(dest)
                    city = dest
                    tourEnd = False
                    break
        loops.append(tour.copy())
        
        # print(tour)
        
    return loops
            
        
def plot_tour(x_coords, y_coords, arc_vars, node_labels=None):
   
    n = len(x_coords)
    if node_labels is None:
        node_labels = list(map(str, range(n)))

    fig, ax = plt.subplots()
    # Plot points
    ax.scatter(x_coords, y_coords, s=50, zorder=2)
    for i, (xi, yi) in enumerate(zip(x_coords, y_coords)):
        ax.text(xi, yi, node_labels[i],
                fontsize=10, ha="right", va="bottom", zorder=3)

    # Plot selected arcs
    
    for i in range(n):
        for j in range(n):
            # Check if arc (i,j) is chosen in the solution
            if arc_vars[i, j].x > 0.5:
                xs = [x_coords[i], x_coords[j]]
                ys = [y_coords[i], y_coords[j]]
                ax.plot(xs, ys, linestyle='-', linewidth=1.5, zorder=1)

    ax.set_aspect('equal')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Tour Visualization')
    plt.tight_layout()
    plt.show()

def TSPSolve():

    m = gp.Model()
    m.modelSense = gp.GRB.MINIMIZE
    # m.setParam('OutputFlag', 0) 
    x = {}
    
    for i in range(N):
        for j in range(N):
            x[i, j] = m.addVar(vtype = gp.GRB.BINARY, name = f"x[{i},{j}]")
    
    m.update()
    
    m.setObjective(sum(sum(Distance[i][j] * x[i, j] for j in range(N)) for i in range(N)))
    
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
    
    
    print ("Planned Trip:")
    
    # for i in range(N):
    #     for j in range(N):
    #         if x[i, j].x >= .0001:
    #             print (Location[i], "--->", Location[j])
    loops = findLoops(x)
    print(loops, "\n")
    while len(loops) > 1:
        for tour in loops:
            m.addConstr(sum(x[tour[i], tour[(i+1)%len(tour)]] for i in range(len(tour)))<= len(tour)-1, name = f"sbtrElim+")
            m.addConstr(sum(x[tour[(i+1)%len(tour)], tour[i]] for i in range(len(tour)))<= len(tour)-1, name = f"sbtrElim-")
            # print(sum(x[tour[i],tour[(i+1)%len(tour)]] for i in range(len(tour)))<= len(tour)-1)
        m.update()
        m.optimize()
        loops = findLoops(x)

        # print(x)
        print ("Optimal Transportation Cost = ", m.objVal)
        
        
        print ("Planned Trip:")
        
        # for i in range(N):
        #     for j in range(N):
        #         if x[i, j].x >= .0001:
        #             print (Location[i], "--->", Location[j])
        print(loops, "\n")
        # break
    # print("hello------------------", findLoops(x))
    m.write('largeTSP.lp')
    plot_tour(loc_x.tolist(), loc_y.tolist(), x)

import matplotlib.pyplot as plt


       

TSPSolve()
