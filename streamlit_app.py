import pandas as pd
import streamlit as st
import logging
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey


logger = logging.getLogger(__name__)


def display_sidebar_ui():
    with st.sidebar:
        st.title("Configuration")
        # checkbox if the CSV contain column names in the first row or not
        values = st.checkbox("CSV contains column names", value=True, key="csv_has_header")
        values = st.checkbox("Use arrows in plot", value=True, key="use_arrows")
        values = st.checkbox("Reverse colors", value=False, key="reverse_colors")
        values = st.slider(
            "Text Size", 1, 100, 10, key="font_size"
        )
        values = st.slider(
            "Text Opacity", 0, 100, 100, key="opacity"
        )
        values = st.slider(
            "Connector Opacity", 0, 100, 100, key="link_opacity"
        )
        values = st.slider(
            "Width", 100, 1000, 1000, key="width"
        )
        values = st.slider(
            "Scale", 0.1, 10, 1, step=0.1, key="scale"
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
            "Sankey thickness", 1, 100, 20, key="sankey_thickness"
        )
        values = st.slider(
            "Line width", 0.0, 5.5, 0.5, step=0.1, key="line_width"
        )


def generate_sankeys():
    if "sankey_data" not in st.session_state:
        return

    for item in st.session_state.sankey_data:
        # Prepare unique values and mapping (excluding the 'value' column)
        value_col = "value"
        df = item["df"]
        df[value_col] = 1
        
        # Get all unique nodes excluding the value column
        nodes = np.unique(df.drop(columns=[value_col]).values, axis=None)
        nodes = pd.Series(index=nodes, data=range(len(nodes)))

        # Create color generator function
        color_palette = getattr(px.colors.qualitative, st.session_state.color_scale)
        def get_color(index):
            base_color = color_palette[index % len(color_palette)]
            # If the color is hex, convert, if it is rgb, convert that one
            if base_color.startswith("#"):
                base_color = base_color.lstrip("#")
                base_color = f"rgba({int(base_color[:2], 16)}, {int(base_color[2:4], 16)}, {int(base_color[4:6], 16)}, {st.session_state.link_opacity / 100})"
            else:
                base_color = base_color.replace("rgb(", "").replace(")", "")
            return base_color

        # Create node colors
        node_colors = [get_color(i) for i in range(len(nodes))]

        # Initialize lists for Sankey diagram
        sources = []
        targets = []
        values = []
        link_colors = []
        scale = st.session_state.scale
        # Generate links between consecutive columns
        columns = [col for col in df.columns if col != value_col]
        for i in range(len(columns) - 1):
            source_col = columns[i]
            target_col = columns[i + 1]

            # Add source-target pairs
            source_indices = [nodes[val] for val in df[source_col]]
            target_indices = [nodes[val] for val in df[target_col]]
            
            sources.extend(source_indices)
            targets.extend(target_indices)
            values.extend(df[value_col])
            if st.session_state.reverse_colors:
                link_colors.extend([get_color(idx) for idx in source_indices])
            else:
                link_colors.extend([get_color(idx) for idx in target_indices])

        fig = go.Figure(
            go.Sankey(
                textfont=dict(
                    color=f"rgba(0,0,0,{st.session_state.opacity})", 
                    size=st.session_state.font_size*scale
                ),
                node={
                    "label": nodes.index,
                    "color": node_colors,
                    "pad": st.session_state.sankey_pad*scale,
                    "line": {
                        "color": "black",
                        "width": st.session_state.line_width*scale,
                    },
                    "thickness": st.session_state.sankey_thickness*scale,
                },
                link={
                    "source": sources,
                    "target": targets,
                    "value": values,
                    "color": link_colors,
                    "arrowlen": 15*scale if st.session_state.use_arrows else 0,
                }
            )
        )

        fig.update_layout(
            title_text="Sankey Diagram",
            height=800*scale,
            width=st.session_state.width*scale,
        )
        st.plotly_chart(fig, use_container_width=True, key=item["index"])
        

def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(page_title="Generate sankey for Milou!")
    st.title("Generate sankey for Milou!")
    if not "sankey_data" in st.session_state:
        st.session_state.sankey_data = []
    if not "csv_has_header" in st.session_state:
        st.session_state.csv_has_header = True
    if not "color_scale" in st.session_state:
        st.session_state.color_scale = "Plotly"
        st.session_state.link_opacity = 100
        st.session_state.use_arrows = True
        st.session_state.reverse_colors = False
        st.session_state.width = 500
        st.session_state.scale = 1

    files_uploaded = st.file_uploader(
        "Upload csv", type=["csv"], accept_multiple_files=True
    )
    if files_uploaded is not None:
        st.session_state.sankey_data = []
        for file_uploaded in files_uploaded:
            # read csv, strings are quotes with "" and columns are comma separated. Ignore extra whitespaces on both ends.
            df = pd.read_csv(file_uploaded, quotechar='"', skipinitialspace=True, header=1 if st.session_state.csv_has_header else 0)
            # clear empty rows
            df = df.dropna(how="any", axis=0)

            st.success(f"Found columns: {[col for col in df.columns]}")
            # Initialize empty dataframe to store all news
            st.session_state.sankey_data.append({"index": file_uploaded.file_id, "df": df})

        # show button to generate sankey
        generate_sankeys()

    display_sidebar_ui()

if __name__ == "__main__":
    main()
