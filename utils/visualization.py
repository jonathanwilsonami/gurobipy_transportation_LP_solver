from bokeh.plotting import figure, output_file, show
import os

class BarPlotter:
    @staticmethod
    def plot(x, y,
             output_html: str = "bar.html",
             output_dir: str = "www",
             title: str = "Bar Chart",
             x_label: str = "x",
             y_label: str = "y",
             width: int = 800,
             height: int = 400):
        cats = [str(v) for v in x]

        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, output_html)

        output_file(path, title=title)
        p = figure(
            x_range=cats,
            title=title,
            toolbar_location=None,
            width=width,
            height=height,
        )
        p.vbar(x=cats, top=y, width=0.8)

        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.xaxis.axis_label = x_label
        p.yaxis.axis_label = y_label
        p.xaxis.major_label_orientation = 1.0

        show(p)
