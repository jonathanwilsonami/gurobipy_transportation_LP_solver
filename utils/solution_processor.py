import re
import polars as pl

class SolutionExtractor:
    # regex for extracting out indx
    VAR_RE = re.compile(r"^x_(\d+)_(\d+)_(\d+)$")

    def __init__(self, model, zero_based: bool = True):
        self.model = model
        self.zero_based = zero_based

    def to_df(self) -> pl.DataFrame:
        records = []
        for v in self.model.getVars():
            m = self.VAR_RE.match(v.VarName)
            if not m:
                continue
            f, c, r = (int(m.group(i)) for i in (1, 2, 3))
            if self.zero_based:
                f, c, r = f - 1, c - 1, r - 1
            records.append({
                "facility": f,
                "chip":     c,
                "region":   r,
                "value":    v.X
            })
        return pl.DataFrame(records)


class SolutionAggregator:
    def __init__(self, df: pl.DataFrame):
        self.df = df

    def by_group(self,
                 group_col: str,
                 value_col: str = "value",
                 alias: str = "total_units",
                 sort_desc: bool = True) -> pl.DataFrame:
        agg = (
            self.df
            .group_by(group_col)
            .agg(pl.col(value_col).sum().alias(alias))
        )
        if sort_desc:
            agg = agg.sort(alias, descending=True)
        return agg