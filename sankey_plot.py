import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import yaml
import numpy as np
import networkx as nx

def brighten_color(hex_color, factor=1.1):
    # Convert HEX to RGB
    rgb = mcolors.hex2color(hex_color)  # Gives values between 0 and 1
    # Brighten the RGB values
    brighter_rgb = tuple(min(1, channel * factor) for channel in rgb)
    # Convert back to HEX
    return mcolors.to_hex(brighter_rgb)

class SankeyContent:
    def __init__(self, config):
        nodes = config["nodes"]
        self.links = config["links"]
        self.values = np.ones(len(self.links)) * -1
        self.nb_level = len(nodes)
        self.required = set(config["required"])
        self.optional = set(config["optional"])
        self.auto_generated = set(config["auto_generated"])
        colors_id = [[idx] * len(nodes[idx]) for idx in range(len(nodes))]
        self.nodes = [node for sublist in nodes for node in sublist]
        colors_id = [color for sublist in colors_id for color in sublist]
        cmap = plt.get_cmap("Pastel1")
        self.node_colors = [mcolors.to_hex(cmap(i)[:3]) for i in colors_id]
        self.link_colors = [brighten_color(mcolors.to_hex(cmap(colors_id[self.nodes.index(link[0])])[:3])) for link in self.links]        

        # build graph using networkx
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.nodes)
        for i, link in enumerate(self.links):
            self.G.add_edge(link[0], link[1], value=0)
        

    def read_values(self, yaml_file):
        data = yaml.load(open(yaml_file), Loader=yaml.FullLoader)
        for key in data.keys():
            assert key in set(self.nodes), f"Key {key} not found in config file."
        for required_key in self.required:
            assert required_key in data.keys(), f"Required key {required_key} not found in config file."
            self.G.nodes[required_key]["value"] = data[required_key]

    def convert_format(self):
        source, target, values, link_colors = [], [], [], []
        try:
            for i, link in enumerate(self.links):
                if self.values[i] <= 0:
                    continue
                source.append(self.nodes.index(link[0]))
                target.append(self.nodes.index(link[1]))
                link_colors.append(self.link_colors[i])
        except ValueError:
            print(f"Node not found in list of nodes: {link[0]} or {link[1]}")
        return source, target, values, link_colors


# read nodes from yaml file
data = yaml.load(open("data/config.yaml"), Loader=yaml.FullLoader)

# Create SankeyContent object
sankey = SankeyContent(data)

sankey.read_values("input/artur.yaml")


# Create Sankey plot
fig = go.Figure(go.Sankey(
    node=dict(
        pad=20,  # Space between nodes
        thickness=20,  # Node thickness
        line=dict(color="black", width=0.5),
        label=sankey.nodes,
        color=sankey.node_colors  # Automatically generated colors for nodes
        align="left"
    ),
    link=dict(
        source=links["source"],
        target=links["target"],
        value=links["value"],
        color=link_colors  # Automatically generated colors for links
    )
))

# Update layout
fig.update_layout(
    title_text="Income and Expense Flow with Automatic Colors",
    title_font_size=20,
    font=dict(size=12, color="black"),
    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
    plot_bgcolor="white"
)

fig.show()

fig.write_image("/Users/artur/Documents/Github/finance/output/sankey_plot.png")
fig.write_html("/Users/artur/Documents/Github/finance/output/sankey_plot.html")