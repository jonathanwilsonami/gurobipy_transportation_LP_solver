import gurobipy as gp

def ncaa_solver(num_seats, media_ratio=None):
    model = gp.Model("NCAA_tickets")
    model.modelSense = gp.GRB.MAXIMIZE
    model.setParam('OutputFlag', 0)

    media = model.addVar(lb=0, vtype = gp.GRB.CONTINUOUS, name="Media")
    uni = model.addVar(lb=0, vtype = gp.GRB.CONTINUOUS, name="Uni")
    pub = model.addVar(lb=0, vtype = gp.GRB.CONTINUOUS, name="Pub")

    model.setObjective(45*uni + 100*pub)

    # Constraints
    # Total seats available
    total_seats = model.addConstr(media + uni + pub <= num_seats, name="TotalSeats")

    

    # Half as many university seats as public seats
    uni_public = model.addConstr(uni - 0.5 * pub >= 0, name="UniPublic")

    # Media constraints
    if media_ratio is None:
        # 500 media seats
        min_media = model.addConstr(media >= 500, name="MinMedia")
    else:
        # Ratio
        min_media = model.addConstr(media >= media_ratio * uni, name="MinMedia")

    # Optimize
    model.optimize()

    results = {
        'media': media.X,
        'uni': uni.X,
        'pub': pub.X,
        'revenue': model.ObjVal,
        'duals': {
            'TotalSeats': total_seats.Pi,
            'MediaMin': min_media.Pi,
            'UniPublic': uni_public.Pi
        }
    }
    return results

# a. What is the optimal seat allocation?
print("===============(a)=====================")
base_case = ncaa_solver(10000)
print("Optimal seat allocation")
print(f"Media seats: {base_case['media']:.0f}")
print(f"University seats: {base_case['uni']:.0f}")
print(f"Public seats: {base_case['pub']:.0f}")
print(f"Maximum Revenue: ${base_case['revenue']:.0f}")
print("===============(b)=====================")


# b. What is the marginal cost to the NCAA of each seat guaranteed to the media?
print(f"Marginal cost to the NCAA of each seat guaranteed to the media: ${base_case['duals']['MediaMin']:.0f}")
print("================(c)====================")

# c. Suppose that there is an alternative arrangement of the arena that can provide 15,000 seats.
# How much additional revenue would be gained from the expanded seating? How much would it
# be for 20,000 seats?
# Case 1: 15,000 seats
case_15000 = ncaa_solver(15000)
case_15000_add_rev = case_15000['revenue'] - base_case['revenue']
print(f"Case 1: 15,000 seats: An additional ${case_15000_add_rev:.0f}")
print()


# Case 2: 20,000 seats
case_20000 = ncaa_solver(20000)
case_20000_add_rev = case_20000['revenue'] - base_case['revenue']
print(f"Case 1: 20,000 seats: An additional ${case_20000_add_rev:.0f}")
print("================(d)====================")
    

# d. Some coaches want the NCAA to restrict media seats to 20% of those allocated for universities.
# Could this policy change the optimal solution? How about 10%?
# Case 1: Media seats <= 20% of University seats
print("Case 1: Media seats to 20 percent of those allocated for universities")
case_20_perc = ncaa_solver(10000, .2)
print(f"Media seats: {case_20_perc['media']:.0f}")
print(f"University seats: {case_20_perc['uni']:.0f}")
print(f"Public seats: {case_20_perc['pub']:.0f}")
print(f"Maximum Revenue: ${case_20_perc['revenue']:.0f}")
print()

# Case 2: Media seats <= 10% of University seats
print("Case 2: Media seats to 10 percent of those allocated for universities")
case_10_perc = ncaa_solver(10000, .1)
print(f"Media seats: {case_10_perc['media']:.0f}")
print(f"University seats: {case_10_perc['uni']:.0f}")
print(f"Public seats: {case_10_perc['pub']:.0f}")
print(f"Maximum Revenue: ${case_10_perc['revenue']:.0f}")
print()

# Optimal seat allocation
# Media seats: 500
# University seats: 3167
# Public seats: 6333
# Maximum Revenue: $775833
# ====================================
# Marginal cost to the NCAA of each seat guaranteed to the media: $-82
# ====================================
# Case 1: 15,000 seats: An additional $408333

# Case 1: 20,000 seats: An additional $816667
# ====================================
# Case 1: Media seats to 20 percent of those allocated for universities
# Media seats: 625
# University seats: 3125
# Public seats: 6250
# Maximum Revenue: $765625

# Case 2: Media seats to 10 percent of those allocated for universities
# Media seats: 323
# University seats: 3226
# Public seats: 6452
# Maximum Revenue: $790323