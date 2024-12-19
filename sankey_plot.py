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
        self.nb_level = len(nodes)
        self.required = set(config["required"])
        self.optional = set(config["optional"])
        self.auto_generated = list(config["auto_generated"])
        self.force_computation = list(config["force_computation"])
        colors_id = [[idx] * len(nodes[idx]) for idx in range(len(nodes))]
        self.nodes = [node for sublist in nodes for node in sublist]
        colors_id = [color for sublist in colors_id for color in sublist]
        cmap = plt.get_cmap("Pastel1")
        self.node_colors = [mcolors.to_hex(cmap(i)[:3]) for i in colors_id]
        self.link_colors = [brighten_color(mcolors.to_hex(cmap(colors_id[self.nodes.index(link[0])])[:3])) for link in self.links]        

        # build graph using networkx
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.nodes, value=0.0)
        for i, link in enumerate(self.links):
            self.G.add_edge(link[0], link[1], value=0)
        
        self.formulas = config["formulas"]

    def read_values(self, yaml_file):
        data = yaml.load(open(yaml_file), Loader=yaml.FullLoader)
        for key in data.keys():
            assert key in set(self.nodes), f"Key {key} not found in config file."
        # Fill value for required nodes
        for required_key in self.required:
            assert required_key in data.keys(), f"Required key {required_key} not found in config file."
            self.G.nodes[required_key]["value"] = data[required_key]
        # Fill value for optional nodes
        for optional_key in self.optional:
            if optional_key in data.keys():
                self.G.nodes[optional_key]["value"] = data[optional_key]
        # Fill value for auto-generated nodes using formulas (if not already filled)
        for auto_generated_key in self.auto_generated:
            if auto_generated_key not in data.keys() or auto_generated_key in self.force_computation:
                formula = self.formulas[auto_generated_key]
                formula = formula.replace(" ", "")
                # split formula into elements and operators
                elements = []
                operators = []
                start = 0
                for i, char in enumerate(formula):
                    if char in ["+", "-"]:
                        elements.append(formula[start:i])
                        operators.append(char)
                        start = i + 1
                elements.append(formula[start:])
                # calculate value
                value = 0
                for i, element in enumerate(elements):
                    if element in self.nodes:
                        if i == 0:
                            value = self.G.nodes[element]["value"]
                        else:
                            if operators[i - 1] == "+":
                                value += self.G.nodes[element]["value"]
                            elif operators[i - 1] == "-":
                                value -= self.G.nodes[element]["value"]
                    else:
                        value += float(element)
                        
                self.G.nodes[auto_generated_key]["value"] = value

        # Fill value for links     
        for i, link in enumerate(self.links):
            print(f"Processing link {link[0]} -> {link[1]}")
            print(list(nx.dfs_edges(self.G, link[1], depth_limit=1)))
            print(len(list(nx.dfs_edges(self.G, link[1], depth_limit=1))), len(list(nx.edge_dfs(self.G, link[1], orientation="reverse"))))
            if len(list(nx.dfs_edges(self.G, link[0], depth_limit=1))) == 1 or len(list(nx.edge_dfs(self.G, link[1], orientation="reverse"))) == 1:
                self.G.edges[link[0], link[1]]["value"] = min(self.G.nodes[link[0]]["value"], self.G.nodes[link[1]]["value"])
            else:
                print(f"Node {link[0]} or {link[1]} has more than one child/parent.")
                raise ValueError()
                
        

    def convert_format(self):
        source, target, values, link_colors = [], [], [], []
        try:
            for i, link in enumerate(self.links):
                if self.G.edges[link[0], link[1]]["value"] <= 0:
                    print(f"Skipping {link[0]} -> {link[1]}")
                    continue
                source.append(self.nodes.index(link[0]))
                target.append(self.nodes.index(link[1]))
                values.append(self.G.edges[link[0], link[1]]["value"])
                link_colors.append(self.link_colors[i])
        except ValueError:
            print(f"Node not found in list of nodes: {link[0]} or {link[1]}")
        return source, target, values, link_colors


# read nodes from yaml file
data = yaml.load(open("data/config.yaml"), Loader=yaml.FullLoader)

# Create SankeyContent object
sankey = SankeyContent(data)

sankey.read_values("input/sven.yaml")

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

fig.write_image("/Users/jesslen/Documents/Github/Finance/output/sankey_plot.png")
fig.write_html("/Users/jesslen/Documents/Github/Finance/output/sankey_plot.html")