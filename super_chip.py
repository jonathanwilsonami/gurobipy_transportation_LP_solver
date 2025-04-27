from gurobipy import *
import polars as pl

# User defined classes and functions - to keep things clean and tidy
# genAI copilot used to refactor code to save me countless hours of cleaning up code 
# Original code is archived for reference 
from utils.data_loader import DataLoader
from utils.report_generator import ComparativeReport
from utils.solution_processor import SolutionExtractor, SolutionAggregator
from utils.visualization import BarPlotter
from utils.sensitivity_processor import (
    ConstraintSensitivityExtractor,
    VariableSensitivityExtractor
)


""" -------------------------------------------------------------------------------------
                                ___LP Model___
------------------------------------------------------------------------------------------
""" 
##############################
# Model Solver 
##############################
def super_chip_solve(supply, demand, costs, model_name, case="alternative", extra_capacity=None):
    m = Model(model_name)
    m.modelSense = GRB.MINIMIZE
    # m.setParam('outputFlag', 0)

    shipping_cost, prod_cost = costs
    n_suppliers = 5
    n_chips = 30
    n_regions = 23 

    # For calculating adding extra capacity per facility 
    if extra_capacity is None:
        extra_capacity = [0] * n_suppliers

    effective_supply = [
        supply[f] + extra_capacity[f]
        for f in range(n_suppliers)
    ]

    x = {}
    """ 
    ___Decision variables___
    x_f_c_r - number of units of chip type c shipped from facility f to region r

    Where
        f is the facility 
        c is the chip type
        r is the region
    """
    for f in range(n_suppliers):
        for c in range(n_chips):
            for r in range(n_regions):
                x[f, c, r] = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name=f"x_{f+1}_{c+1}_{r+1}")
    
    """ 
    ___Objective Function___ 
    Minimize the total cost of operations for Super Chip company by minimizing 
    production and shipping costs of 30 different chip products to 23 different regions from 
    5 different facilities. 

    Where 
        shipping_cost[f][c][r] is the shipping cost f_c_r -> shipping_cost_f_c_r
        prod_cost[f][c] is the Production cost f_c -> shipping_cost_f_c
    """
    m.setObjective(
        quicksum(
            (prod_cost[f][c] + shipping_cost[f][c][r]) 
            * x[f, c, r]
            for f in range(n_suppliers)
            for c in range(n_chips)
            for r in range(n_regions)
        )
    )

    """ 
    ___Base Case Constraints___ 
    The base case repersents each facility producing each of the 30 types of chips at levels that are proportional to 
    the facility's total portion of production capacity. See the Suppply constraint.
    """
    if case == "base":
        total_supply = sum(supply)
        facility_capacity_proportions = [cap_f / total_supply for cap_f in supply]

        # Total demand per chip across all regions
        total_demand_by_chip = {
            c: sum(demand[r][c] for r in range(n_regions))
            for c in range(n_chips)
        }
        total_demand_for_chips = sum(total_demand_by_chip.values())
        print(total_demand_for_chips)
        
        """ 
        ___Supply Constraint___ 
        Binding constraint is added here to ensure that production levels are proportional to the facility's total proportion of 
        production capacity. Here total_demand_for_chips is the sum of all demand for all chips for each region.  
        """
        for f in range(n_suppliers):
            m.addConstr(
                quicksum(
                    x[f, c, r]
                    for c in range(n_chips)
                    for r in range(n_regions)
                )
                == facility_capacity_proportions[f] * total_demand_for_chips,
                name=f"supply_f{f+1}"
            )
        """ 
        ___Demand Constraint___ 
        The available supply must meet the following demands based on region and chip type. 
        EX: for r,c,r --> demand_rx_cx: sum(x_f_c_r) >= demand_for_r_c
        demand_r1_c2: x_1_2_1 + x_2_2_1 + x_3_2_1 + x_4_2_1 + x_5_2_1 >= 2.387
        """
        for c in range(n_chips):
            for r in range(n_regions):
                m.addConstr(
                    quicksum(x[f, c, r] for f in range(n_suppliers))
                    >= demand[r][c],
                    name=f"demand_r{r+1}_c{c+1}"
                )
        """ 
        ___Alternative Case Constraints___ 
        The alternative case foregoes the proportional production capacities and instead allows the solver to decide 
        which facility should produce how much while ensuring the following constraints are met.
        """
    elif case == "alternative":
        """ 
        ___Supply Constraint___ 
        For each facility f and chip type c the total units shipped to each region shall not exceed the capacity of 
        what the facility can produce. Supply[f] is the supply available for facility f. 
        """
        for f in range(n_suppliers):
            m.addConstr(
                quicksum(
                    x[f, c, r]
                    for c in range(n_chips)
                    for r in range(n_regions)
                )
                <= effective_supply[f],
                name=f"supply_f{f+1}"
            )
        
        """ 
        ___Demand Constraint___ 
        The available supply must meet the following demands based on region and chip type. 
        EX: for r,c,r --> demand_rx_cx: sum(x_f_c_r) >= demand_for_r_c
        demand_r1_c2: x_1_2_1 + x_2_2_1 + x_3_2_1 + x_4_2_1 + x_5_2_1 >= 2.387
        """
        for c in range(n_chips):
            for r in range(n_regions):
                m.addConstr(
                    quicksum(x[f,c,r] for f in range(n_suppliers))
                    >= demand[r][c],
                    name=f"demand_r{r+1}_c{c+1}"
                )
    else:
        # for testing
        print("Testing....")
    m.update()
    m.optimize()  
    m.write(f"models_and_solutions/super_chip_{model_name}.lp")
    m.write(f"models_and_solutions/super_chip_{model_name}.sol")

    return(m)
""" -------------------------------------------------------------------------------------
                                ___Data Wrangling___
------------------------------------------------------------------------------------------
""" 
##############################
# Extract Data
##############################
prod_cap_df, demand_df, shipping_cost_df, prod_cost_df = (
    DataLoader("../data/SuperChipData.xlsx")
    .load()
)

##############################
# Supply
##############################
# [f1,f2,...f5]
prod_cap = prod_cap_df["Computer Chip Production Capacity (thousands per year)"].to_list()

# Facility map
facility_list = prod_cap_df["Facility"].to_list()
facility_to_idx = {name: idx for idx, name in enumerate(facility_list)}
indx_to_facility = {idx: name for idx, name in enumerate(facility_list)}

##############################
# Demand
##############################
demand_df_wide = demand_df.pivot(
    values="Yearly Demand (thousands)",
    index="Sales Region",
    on="Computer Chip"
)

# demand[r][c] -> demand in thousands 
demand = {
    int(row["Sales Region"]) - 1: {
        int(chip) - 1: row[chip]
        for chip in row.keys()
        if chip != "Sales Region"
    }
    for row in demand_df_wide.to_dicts()
}

##############################
# Shipping Cost
##############################
# shipping_cost[f][c][r] -> shipping_cost_f_c_r
shipping_cost_df = shipping_cost_df.with_columns(
    pl.col("Facility")
      .cast(pl.Categorical)
      .to_physical()
      .alias("facility_idx")
)

shipping_cost_df = shipping_cost_df.drop("Facility")

shipping_wide = shipping_cost_df.pivot(
    values="Shipping Cost ($ per chip)",
    index=["facility_idx", "Computer Chip"],
    on="Sales Region",
)

shipping_cost = {}
for row in shipping_wide.to_dicts():
    f = row.pop("facility_idx")
    c = int(row.pop("Computer Chip")) - 1
    reg_map = {
        int(region) - 1: row[region]
        for region in row
    }
    shipping_cost.setdefault(f, {})[c] = reg_map

##############################
# Production Cost
##############################
# prod_cost[f][c] -> prod_cost
prod_cost_df = prod_cost_df.with_columns(
    pl.col("Facility")
      .cast(pl.Categorical)
      .to_physical()
      .alias("facility_idx")
)

prod_cost_df = prod_cost_df.drop("Facility")

prod_wide = prod_cost_df.pivot(
    values="Production Cost ($ per chip)",
    index="facility_idx",
    on="Computer Chip",
)

prod_cost = {}
prod_cost = {
    int(row["facility_idx"]): {
        int(chip) - 1: row[chip]
        for chip in row.keys() 
        if chip != "facility_idx"
    }
    for row in prod_wide.to_dicts()
}

""" -------------------------------------------------------------------------------------
                                ___Analysis___
------------------------------------------------------------------------------------------
""" 

"""
##############################
# Background
##############################
Super Chip Inc is a fictitious chip manufacture based in VA.
They have five manufacturing facilities Alexandria, Richmond, Norfolk, Roanoke, and Charolottesville.
Super Chip makes 30 different chip products and distributes to 23 different sales regions across the U.S.
Each facility has different production capacity levels. 
Each facility has different equipment and costs for set-up processes. 
There area also variations in shipping distances and shipping material requirements, different shipping costs 

##############################
# Problem Statement
##############################
Super Chip would like a recommendation as to how they should carry out their production and
distribution operations for the following fiscal year. Included in the recommendation, Super Chip is
interested in evaluating certain strategic-level questions:
"""

""""
##############################
# #1 - Is the current proportional production method good or bad? 
##############################
Currently, each facility produces each of the 30 types of chips at levels that are proportional to
the facility's total portion of production capacity. For example, if facility x has y% of the total
production capacity across all facilities, then facility x currently produces y% of every chip's total
demand. 

Would you recommend an alternative production policy? 

If so, how would the new policy compare to the current one with respect to costs?

Solution approach: 
- 
"""
##########################################################################################
# Base Case - Current Method

# Alt Case - Alternative Method or AOA

# Basis for a new reco to alternative production policy
########################################################################################################################

model_base = super_chip_solve(prod_cap, demand, [shipping_cost, prod_cost], "base", "base")
model_alternative = super_chip_solve(prod_cap, demand, [shipping_cost, prod_cost], "alternative")

##########################################################################################
# Comparative Analysis of base case and alternative 
############################################################
ComparativeReport(model_base, model_alternative).generate("comparison_reports/Comparison_Report_Base_Alt.txt")

""""
##############################
# #2 - Which facility to expand and invest in?  
##############################
Super Chip has received additional cash flows that are available for capital investment. 

Based on your recommendation to the question above, if Super Chip was to expand the production
capacity at a single facility by purchasing additional equipment, which facility should receive the
investment of capital? 

How much would a production capacity expansion affect the total costs for production and distribution?

Solution approach: 
- 
"""

base_df = SolutionExtractor(model_base).to_df()
alt_df  = SolutionExtractor(model_alternative).to_df()

# aggregate by facility (or chip/region)
base_by_fac = SolutionAggregator(base_df).by_group("facility")
alt_by_fac  = SolutionAggregator(alt_df).by_group("facility")

# map zero‐based indices back to facility names
facilities_base = [indx_to_facility[i] for i in base_by_fac["facility"].to_list()]
totals_base     = base_by_fac["total_units"].to_list()

facilities_alt = [indx_to_facility[i] for i in alt_by_fac["facility"].to_list()]
totals_alt     = alt_by_fac["total_units"].to_list()

# Distribution of units per facility plot
# BarPlotter.plot(
#     facilities_base,
#     totals_base,
#     output_html="facility_totals_base.html",
#     title="Total Units by Facility (Base Case)",
#     x_label="Facility",
#     y_label="Total Units (thousands)"
# )
# BarPlotter.plot(
#     facilities_alt,
#     totals_alt,
#     output_html="facility_totals_alternative.html",
#     title="Total Units by Facility (Alternative Case)",
#     x_label="Facility",
#     y_label="Total Units (thousands)"
# )

##############################
# Extract data from model
##############################
constraint_df = (
    ConstraintSensitivityExtractor(
        model_alternative,
        indx_to_facility
    )
    .to_df()
    .sort("shadow_price", descending=True)
)
constraint_df.write_csv("constraint_sensitivity_df.csv")

variable_df = VariableSensitivityExtractor(
    model_alternative,
    indx_to_facility
).to_df()
variable_df.write_csv("variable_sensitivity_df.csv")

##############################
# Expanding the production capacity
##############################

"""
constraint	facility	facility_idx	region	chip_type	shadow_price	rhs_sensitivity_low	rhs_sensitivity_high
supply_f5	Charolottesville	5			5.15000000000001	154.257554585153	154.257554585153
supply_f4	Roanoke	4			2.41000000000001	163.331528384279	163.33152838428
supply_f3	Norfolk	3			0.190000000000005	222.312358078602	222.312358078603
supply_f1	Alexandria	1			0	263.145240174673	263.145240174673
							
supply_f2	Richmond	2			-0.829999999999998	235.923318777292	235.923318777293

"""
extra = [0, 235.923318777292, 0, 0, 0]
extra_model = super_chip_solve(prod_cap, demand, [shipping_cost, prod_cost], "expanding_prod", extra_capacity=extra)
constr_alt = model_alternative.getConstrByName("supply_f2")
print(f"Alternative objective value = ${model_alternative.ObjVal*1000:,.2f}")
print("Alt RHS is:", constr_alt.RHS)
print("Alt Pi  is:", constr_alt.Pi)
constr_extra = extra_model.getConstrByName("supply_f2")
print(f"Extra objective value = ${extra_model.ObjVal*1000:,.2f}")
print("RHS is:", constr_extra.RHS)
print("Pi  is:", constr_extra.Pi)  
""""
##############################
# #3 - 10% demand increase cand they handle this? Costs?  
##############################
It is estimated that next year's demand is going to increase by 10% across all of the sales
regions. 

Does Super Chip have sufficient capacity to handle the estimated increase in demand?

If so, what are the associated costs for filling the new demand in comparison to this year's
demand?

Solution approach: 
- create a new demand that add a 10% increase to all demands 
- resolve the alternative case model with this new demand
- evaluate results 
"""
# print(demand[0][1]) # demand[0][1] = 2.17 ----> new_demand[0][1] = 2.387
demand_increase = 1.10  # +10%
new_demand = {
    outer: {
        inner: val * demand_increase
        for inner, val in inner_dict.items()
    }
    for outer, inner_dict in demand.items()
}
demand_increase_model = super_chip_solve(prod_cap, new_demand, [shipping_cost, prod_cost], "new_demand")
ComparativeReport(model_alternative, demand_increase_model).generate("comparison_reports/Comparison_Report_Alt_new_demand.txt")


""""
##############################
# #4 - New tech and which facility? 
##############################
Super Chip is evaluating new manufacturing technologies. It is estimated that one of these new
technologies could reduce production costs for all of the chips by 15%. 

If Super Chip was to evaluate this new manufacturing technology in one of its facilities, which facility should receive
the new technology?

Solution approach: 
- Itereate through the prod_cost for each facility and and reduce the cost by 15%. This assumes the new tech would have been 
applied to this facility.
- Rerun the LP solver for each scenario (each facility) and take the min objective value 
"""
# print("prod before:", prod_cost[0][0])
# print("prod before:", prod_cost[1][0])
# print("prod after:", new_prod_cost[0][0])
# print("prod after:", new_prod_cost[1][0])

models = []
for f in range(5):
    decrease_factor = 0.85 # 1-.15 or 15% decrease in cost 
    facility = f

    new_prod_cost = {
        outer: (
            {
                chip: max(val * decrease_factor, 0) # don't go below 0
                for chip, val in inner_dict.items()
            }
            if outer == facility
            else inner_dict.copy()
        )
        for outer, inner_dict in prod_cost.items()
    }

    new_tech_model = super_chip_solve(prod_cap, demand, [shipping_cost, new_prod_cost], f"new_tech_{facility}")
    ComparativeReport(model_alternative, new_tech_model).generate(f"comparison_reports/Comparison_Report_Alt_new_tech_{facility}.txt")
    models.append(new_tech_model)

def find_min(models):
    min_model = models[0]
    for m in models[1:]:
        if m.ObjVal < min_model.ObjVal:
            min_model = m

    return min_model

model_tech = find_min(models)
print(f"Best objective value = ${model_tech.ObjVal*1000:,.2f}")
ComparativeReport(model_alternative, model_tech).generate("comparison_reports/Comparison_Report_Alt_new_tech.txt")



