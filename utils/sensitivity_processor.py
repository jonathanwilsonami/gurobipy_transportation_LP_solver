import re
import polars as pl

class ConstraintSensitivityExtractor:
    def __init__(
        self,
        model,
        idx_to_facility,
        supply_pattern: str = r"^supply_f(\d+)$",
        demand_pattern: str = r"^demand_r(\d+)_c(\d+)$",
    ):
        self.model = model
        self.idx_to_facility = idx_to_facility
        self.r_supply = re.compile(supply_pattern)
        self.r_demand = re.compile(demand_pattern)

    def to_df(self) -> pl.DataFrame:
        records = []
        for c in self.model.getConstrs():
            name = c.ConstrName
            m_sup = self.r_supply.match(name)
            m_dem = self.r_demand.match(name)

            if not (m_sup or m_dem):
                continue

            supply_idx = int(m_sup.group(1)) if m_sup else None
            demand_idx, chip_idx = (int(m_dem.group(i)) for i in (1, 2)) if m_dem else (None, None)

            records.append({
                "constraint":           name,
                "facility_idx":         supply_idx,
                "facility":             self.idx_to_facility[supply_idx - 1] if supply_idx else None,
                "region":               demand_idx,
                "chip_type":            chip_idx,
                "shadow_price":         c.Pi,
                "rhs_sensitivity_low":  c.SARHSLow,
                "rhs_sensitivity_high": c.SARHSUp,
            })

        schema = [
            ("constraint",           pl.Utf8),
            ("facility_idx",         pl.Int64),
            ("facility",             pl.Utf8),
            ("region",               pl.Int64),
            ("chip_type",            pl.Int64),
            ("shadow_price",         pl.Float64),
            ("rhs_sensitivity_low",  pl.Float64),
            ("rhs_sensitivity_high", pl.Float64),
        ]

        df = pl.DataFrame(records, schema=schema)
        return df


class VariableSensitivityExtractor:
    def __init__(self, model, idx_to_facility, var_prefix: str = "x_"):
        self.model = model
        self.idx_to_facility = idx_to_facility
        self.var_prefix = var_prefix

    def to_df(self) -> pl.DataFrame:
        records = []
        for v in self.model.getVars():
            name = v.VarName
            if not name.startswith(self.var_prefix):
                continue

            parts = name.removeprefix(self.var_prefix).split("_")
            f_idx, c_idx, r_idx = (int(p) for p in parts)

            records.append({
                "variable":             name,
                "facility":             self.idx_to_facility[f_idx - 1],
                "chip_type":            c_idx,
                "region":               r_idx,
                "var_sensitivity_low":  v.SAObjLow,
                "var_sensitivity_high": v.SAObjUp,
            })

        return pl.DataFrame(records)
