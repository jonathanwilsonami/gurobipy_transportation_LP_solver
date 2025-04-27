from pathlib import Path
import pandas as pd
import polars as pl

class DataLoader:
    def __init__(self, file_name: str):
        script_dir = Path(__file__).parent.resolve()
        self.file_path = (script_dir / file_name).resolve()
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    def load(self):
        suffix = self.file_path.suffix.lower()

        if suffix == ".xlsx":
            def _sheet(name):
                return pl.from_pandas(
                    pd.read_excel(self.file_path, engine="openpyxl", sheet_name=name)
                )

            prod_cap_df      = _sheet("Production Capacity")
            demand_df        = _sheet("Sales Region Demand")
            shipping_cost_df = _sheet("Shipping Costs")
            prod_cost_df     = _sheet("Production Costs")

        elif suffix == ".ods":
            pd_df = pd.read_excel(self.file_path, engine="odf")
            prod_cap_df = demand_df = shipping_cost_df = prod_cost_df = pl.from_pandas(pd_df)

        else:
            raise ValueError("Unsupported file format. Use .xlsx or .ods")

        return prod_cap_df, demand_df, shipping_cost_df, prod_cost_df