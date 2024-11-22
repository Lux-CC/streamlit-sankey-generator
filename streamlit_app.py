import pandas as pd
import streamlit as st
import logging
import pandas as pd
import plotly.graph_objects as go
import textwrap

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
        unique_cols = [df[col].unique() for col in df.columns]
        all_values = [item for sublist in unique_cols for item in sublist]

        node_labels = list(pd.unique(all_values))

        label_to_index = {label: i for i, label in enumerate(node_labels)}

        # Create links
        links = []
        for _, row in df.iterrows():
            for i in range(len(row) - 1):
                links.append(
                    {
                        "source": label_to_index[row[i]],
                        "target": label_to_index[row[i + 1]],
                        "value": 1,
                    }
                )

        # Prepare data for the Sankey diagram
        sankey_data = {

            # wrap lines each 40 characters and 80 and 120 etc. (insert \n)
            "node": {"label": [textwrap.fill(label, width=40).replace('\n', '<br>') for label in node_labels]},
            "link": {
                "source": [link["source"] for link in links],
                "target": [link["target"] for link in links],
                "value": [link["value"] for link in links],
            },
        }

        # Create the Sankey diagram
        fig = go.Figure(
            go.Sankey(
                node=dict(
                    pad=st.session_state.sankey_pad,
                    thickness=st.session_state.sankey_thickness,
                    line=dict(color="black", width=st.session_state.line_width),
                    label=sankey_data["node"]["label"],
                    color=st.session_state.node_color,
                ),
                link=dict(
                    source=sankey_data["link"]["source"],
                    target=sankey_data["link"]["target"],
                    value=sankey_data["link"]["value"],
                    # color=st.session_state.link_color,
                ),
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


def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(page_title="Generate sankey for Milou!")
    st.title("Generate sankey!")
    display_sidebar_ui()

    st.session_state.sankey_data = [pd.DataFrame()]

    files_uploaded = st.file_uploader(
        "Upload csv", type=["csv"], accept_multiple_files=True
    )
    if files_uploaded is not None:
        for file_uploaded in files_uploaded:
            df = pd.read_csv(file_uploaded)
            # clear empty rows
            df = df.dropna(how="all")
            st.write(f"Found columns: {[col for col in df.columns]}")
            # Initialize empty dataframe to store all news
            st.session_state.sankey_data.append(df)

    if not st.session_state.sankey_data[0].empty:
        # show button to generate sankey
        if st.button("Generate sankey"):
            generate_sankeys()


if __name__ == "__main__":
    main()
