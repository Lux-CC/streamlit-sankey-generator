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
        # Get HEX color
        st.session_state.node_color = st.color_picker(
            "Column color", on_change=generate_sankeys
        )
        st.session_state.link_color = st.color_picker(
            "Link color", on_change=generate_sankeys
        )
        # # Convert selected labels back to their URLs

        # Get input for graph title
        st.session_state.graph_title = st.text_input(
            "Enter graph title", value="Graph Title", on_change=generate_sankeys
        )

        # Get input for graph subtitle
        st.session_state.graph_subtitle = st.text_input(
            "Enter graph subtitle", value="Graph Subtitle", on_change=generate_sankeys
        )

        # get input sliders for sankey pad and thickness
        st.session_state.sankey_pad = st.slider(
            "Sankey pad", 0, 100, 15, on_change=generate_sankeys
        )
        st.session_state.sankey_thickness = st.slider(
            "Sankey thickness", 0, 100, 20, on_change=generate_sankeys
        )
        st.session_state.line_width = st.slider(
            "Line width", 0.0, 5.5, 0.5, step=0.1, on_change=generate_sankeys
        )
        st.session_state.font_size = st.slider(
            "Font size", 0, 20, 10, step=1, on_change=generate_sankeys
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
            font_size=st.session_state.font_size,
        )
        # output the figure to streamlit
        st.plotly_chart(fig, use_container_width=True)

        # now also create a matplotlib sankey diagram fig
        fig = create_sankey()
        st.pyplot(fig)


# Define a function to create the Sankey diagram
def create_sankey():
    sankey = Sankey(unit=None)  # Disable unit display

    # Define the flows: positive values are inputs, negative are outputs
    # For simplicity, we'll aggregate flows by source
    flows = [80, 60, 50, -50, -30, -40, -60, -20, -30]  # Example flows
    labels = ['Total Sources', 'Coal', 'Natural Gas', 'Nuclear',
              'Residential', 'Commercial', 'Industrial', '', '']
    orientations = [0, 1, 1, 1, 0, 0, 0, 0, 0]

    sankey.add(flows=flows, labels=labels, orientations=orientations, facecolor='blue')
    diagrams = sankey.finish()

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.add_collection(diagrams)
    ax.title.set_text('Energy Flow Sankey Diagram')
    plt.tight_layout()
    return fig
                




def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(page_title="Generate sankey for Milou!")
    st.title("Generate sankey for Milou!")
    display_sidebar_ui()

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
        if st.button("Generate sankey"):
            generate_sankeys()


if __name__ == "__main__":
    main()
