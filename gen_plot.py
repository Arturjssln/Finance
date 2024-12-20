from sankey_plot import SankeyContent
import plotly.graph_objects as go
import yaml
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Generate Sankey plot from yaml file")
parser.add_argument("--input", type=str, help="Input yaml file", default="data/example.yaml")
parser.add_argument("--config", type=str, help="Config yaml file", default="data/config.yaml")
parser.add_argument("--output_dir", type=str, help="Output directory", default="data")
args = parser.parse_args()

if __name__ == "__main__":
    # read nodes from yaml file
    data = yaml.load(open(args.config), Loader=yaml.FullLoader)

    # Create SankeyContent object
    sankey = SankeyContent(data)

    sankey.read_values(args.input)

    source, target, values, link_colors = sankey.convert_format()

    # Create Sankey plot
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=20,  # Space between nodes
            thickness=20,  # Node thickness
            line=dict(color="black", width=0.5),
            label=sankey.nodes,
            color=sankey.node_colors,  # Automatically generated colors for nodes
            align="left"
        ),
        link=dict(
            source=source,
            target=target,
            value=values,
            color=link_colors  # Automatically generated colors for links
        )
    ), layout=go.Layout(width=1000, height=500))

    # Update layout
    fig.update_layout(
        title_text="Example Sankey Plot",
        title_font_size=20,
        font=dict(size=12, color="black"),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        plot_bgcolor="white"
    )
    try:
        fig.show()
    except:
        pass
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    fig.write_image(Path(args.output_dir) / "sankey_plot.png")
    fig.write_html(Path(args.output_dir) / "sankey_plot.html")