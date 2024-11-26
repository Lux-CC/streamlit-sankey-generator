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
    # check if st.session_state.sankey_data is set
    if "sankey_data" not in st.session_state:
        return

    for df in st.session_state.sankey_data:
        # Prepare unique values and mapping
        nodes = np.unique(df, axis=None)
        nodes = pd.Series(index=nodes, data=range(len(nodes)))
        # rename the first column "source and the last target"
        df = df.rename(columns={df.columns[0]: "source", df.columns[-1]: "target"})
        # add a column "value" with value 1
        df["value"] = 1

        fig = go.Figure(
            go.Sankey(
                textfont=dict(color=f"rgba(0,0,0,{st.session_state.opacity})", size=st.session_state.font_size),
                node={
                    "label": nodes.index,
                    "color": [
                        px.colors.qualitative.Plotly[
                            i % len(px.colors.qualitative.Plotly)
                        ]
                        for i in nodes
                    ],
                    "pad": st.session_state.sankey_pad,  # 15 pixels
                    "thickness": st.session_state.sankey_thickness,  # 20 pixels
                },
                link={
                    "source": nodes.loc[df["source"]],
                    "target": nodes.loc[df["target"]],
                    "value": df["value"],
                    "color": [
                        px.colors.qualitative.Plotly[
                            i % len(px.colors.qualitative.Plotly)
                        ]
                        for i in nodes.loc[df["target"]]
                    ],
                },
            )
        )
        st.session_state.fig = fig

        # Update layout and show figure
        fig.update_layout(
            title_text="Sankey Diagram",
        )
        # output the figure to streamlit
        st.plotly_chart(st.session_state.fig, use_container_width=True)

            


def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(page_title="Generate sankey for Milou!")
    st.title("Generate sankey for Milou!")
    st.session_state.sankey_data = []

    files_uploaded = st.file_uploader(
        "Upload csv", type=["csv"], accept_multiple_files=True
    )
    if files_uploaded is not None:
        for file_uploaded in files_uploaded:
            df = pd.read_csv(file_uploaded)
            # clear empty rows
            df = df.dropna(how="all")
            # drop second column
            df = df.drop(df.columns[1], axis=1)
            st.write(f"Found columns: {[col for col in df.columns]}")
            # Initialize empty dataframe to store all news
            st.session_state.sankey_data.append(df)

    if st.session_state.sankey_data:
        # show button to generate sankey
        generate_sankeys()

    display_sidebar_ui()

if __name__ == "__main__":
    main()
