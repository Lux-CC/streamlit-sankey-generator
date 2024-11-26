import pandas as pd
import streamlit as st
import logging
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey


logger = logging.getLogger(__name__)


def display_sidebar_ui():
    with st.sidebar:
        st.title("Configuration")
        values = st.slider(
            "Text Size", 0, 100, 10, key="font_size"
        )
        values = st.slider(
            "Text Opacity", 0, 100, 100, key="opacity"
        )
        qualitative_color_scales = [scale for scale in dir(px.colors.qualitative) if not scale.startswith("__")]

        values = st.selectbox(
            "Select a colorscale",
            # get list of px.colors.qualitative colors
            qualitative_color_scales,
            key="color_scale",
        )


        # get input sliders for sankey pad and thickness
        values = st.slider(
            "Sankey pad", 0, 100, 15, key="sankey_pad"
        )
        values = st.slider(
            "Sankey thickness", 0, 100, 20, key="sankey_thickness"
        )
        values = st.slider(
            "Line width", 0.0, 5.5, 0.5, step=0.1, key="line_width"
        )


def generate_sankeys():
    if "sankey_data" not in st.session_state:
        return

    for df in st.session_state.sankey_data:
        # Prepare unique values and mapping
        nodes = np.unique(df, axis=None)
        nodes = pd.Series(index=nodes, data=range(len(nodes)))

        # add a column "value" with value 1
        df["value"] = 1

        # Create color generator function
        color_palette = getattr(px.colors.qualitative, st.session_state.color_scale)
        def get_color(index):
            return color_palette[index % len(color_palette)]

        # Create node colors
        node_colors = [get_color(i) for i in nodes]

        # Initialize lists for Sankey diagram
        sources = []
        targets = []
        values = []
        link_colors = []

        # Generate links between consecutive columns
        for i in range(len(df.columns) - 1):
            if i == len(df.columns) - 2:  # Last pair of columns
                source_col = df.columns[i]
                target_col = df.columns[i + 1]
            else:
                source_col = df.columns[i]
                target_col = df.columns[i + 1]

            # Add source-target pairs
            sources.extend(list(nodes.loc[df[source_col]]))
            targets.extend(list(nodes.loc[df[target_col]]))
            values.extend(list(df["value"]))
            link_colors.extend([get_color(i) for i in nodes.loc[df[target_col]]])

        fig = go.Figure(
            go.Sankey(
                textfont=dict(
                    color=f"rgba(0,0,0,{st.session_state.opacity})", 
                    size=st.session_state.font_size
                ),
                node={
                    "label": nodes.index,
                    "color": node_colors,
                    "pad": st.session_state.sankey_pad,
                    "thickness": st.session_state.sankey_thickness,
                },
                link={
                    "source": sources,
                    "target": targets,
                    "value": values,
                    "color": link_colors
                }
            )
        )

        fig.update_layout(
            title_text="Sankey Diagram",
        )

        st.session_state.fig = fig
        

def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(page_title="Generate sankey for Milou!")
    st.title("Generate sankey for Milou!")
    if not "sankey_data" in st.session_state:
        st.session_state.sankey_data = []
    if not "color_scale" in st.session_state:
        st.session_state.color_scale = "Plotly"

    files_uploaded = st.file_uploader(
        "Upload csv", type=["csv"], accept_multiple_files=True
    )
    if files_uploaded is not None:
        st.session_state.sankey_data = []
        for file_uploaded in files_uploaded:
            df = pd.read_csv(file_uploaded)
            # clear empty rows
            df = df.dropna(how="all")
            
            st.write(f"Found columns: {[col for col in df.columns]}")
            # Initialize empty dataframe to store all news
            st.session_state.sankey_data.append(df)

    if st.session_state.sankey_data:
        # show button to generate sankey
        generate_sankeys()
        st.plotly_chart(st.session_state.fig, use_container_width=True, key="my_chart")

    display_sidebar_ui()

if __name__ == "__main__":
    main()
