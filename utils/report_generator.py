import datetime

class ComparativeReport:
    def __init__(self, model_base, model_alt):
        self.base = model_base
        self.alt  = model_alt
        self.metrics = {
            "Objective (x1000 USD)": lambda m: m.ObjVal * 1000,
            "Solve Time (s)"       : lambda m: m.Runtime,
            "Vars"                 : lambda m: m.NumVars,
            "Constrs"              : lambda m: m.NumConstrs,
        }

    def generate(self, filename="comparison_report.txt"):
        base_name = self.base.ModelName
        alt_name  = self.alt.ModelName

        rows = []
        for label, fn in self.metrics.items():
            b = fn(self.base)
            a = fn(self.alt)
            rows.append((label, b, a, b - a))

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = (
            f"Comparison Report\n"
            f"Models: {base_name}  vs.  {alt_name}\n"
            f"Generated: {now}\n"
            + "="*72 + "\n"
        )
        col_hdr   = f"{'Metric':30s} | {base_name:>12s} | {alt_name:>12s} | {'Diff':>12s}\n"
        separator = "-"*72 + "\n"

        with open(filename, "w") as f:
            f.write(header)
            f.write(col_hdr)
            f.write(separator)

            for label, b, a, diff in rows:
                if "Time" in label:
                    fmt = "{:>12.2f}"
                else:
                    fmt = "{:>12,.2f}"
                f.write(
                    f"{label:30s} | "
                    + fmt.format(b) + " | "
                    + fmt.format(a) + " | "
                    + fmt.format(diff)
                    + "\n"
                )

            for model, name in ((self.base, base_name), (self.alt, alt_name)):
                f.write(f"\n=== Variables for {name} ===\n")
                for v in model.getVars():
                    f.write(
                        f"{v.VarName:30s}  "
                        f"X={v.X:>8.2f}  "
                        f"RC={v.RC:>8.2f}  "
                        f"ObjCo={v.Obj:>8.2f}\n"
                    )

            for model, name in ((self.base, base_name), (self.alt, alt_name)):
                f.write(f"\n=== Constraints for {name} ===\n")
                for c in model.getConstrs():
                    f.write(
                        f"{c.ConstrName:30s}  "
                        f"Slack={c.Slack:>8.2f}  "
                        f"Pi={c.Pi:>8.2f}  "
                        f"Sense={c.Sense:>2s}  "
                        f"RHS={c.RHS:>8.2f}\n"
                    )

            f.write("\n" + "="*72 + "\n")

        print(f"Comparative report written to {filename}")