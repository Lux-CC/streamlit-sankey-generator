import pandas as pd
import streamlit as st
import logging
import pandas as pd
import plotly.graph_objects as go
logger = logging.getLogger(__name__)


def display_sidebar_ui():
    with st.sidebar:
        st.title("Configuration")
        # colors = {
        #     "https://www.snowflake.com/feed/": "Snowflake Official",
        #     "https://rss.aws-news.com/custom_feeds/FEzdG/rss": "AWS Snowflake News",
        # }

        # # Get the list of feed URLs and labels
        # rss_feeds = list(rss_feed_labels.keys())
        # feed_labels = list(rss_feed_labels.values())

        # # Create a dictionary to map labels back to their URLs for later use
        # label_to_url = {label: url for url, label in rss_feed_labels.items()}

        # Get HEX color
        selected_color = st.color_picker("Select color")
        # # Convert selected labels back to their URLs
        st.session_state.color = selected_color

        # Get input for graph title
        st.session_state.graph_title = st.text_input("Enter graph title", value="Graph Title")

        # Get input for graph subtitle
        st.session_state.graph_subtitle = st.text_input("Enter graph subtitle", value="Graph Subtitle")

        # get input sliders for sankey pad and thickness
        st.session_state.sankey_pad = st.slider("Sankey pad", 0, 100, 15)
        st.session_state.sankey_thickness = st.slider("Sankey thickness", 0, 100, 20)
        st.session_state.line_width = st.slider("Line width", 0.0, 5.0, 0.5, step=0.1)
        st.session_state.font_size = st.slider("Font size", 0, 20, 10, step=1)






def generate_sankey(df):

    # Prepare unique values and mapping
    unique_cols = [df[col].unique() for col in df.columns]
    all_values = [item for sublist in unique_cols for item in sublist]

    node_labels = list(pd.unique(all_values))
    label_to_index = {label: i for i, label in enumerate(node_labels)}
    
    # Create links
    links = []
    for _, row in df.iterrows():
        for i in range(len(row) - 1):
            links.append({'source': label_to_index[row[i]],
                          'target': label_to_index[row[i + 1]],
                          'value': 1})
    
    # Prepare data for the Sankey diagram
    sankey_data = {
        'node': {
            'label': node_labels
        },
        'link': {
            'source': [link['source'] for link in links],
            'target': [link['target'] for link in links],
            'value': [link['value'] for link in links],
        }
    }
    
    # Create the Sankey diagram
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=st.session_state.sankey_pad,
            thickness=st.session_state.sankey_thickness,
            line=dict(color="black", width=st.session_state.line_width),
            label=sankey_data['node']['label']
        ),
        link=dict(
            source=sankey_data['link']['source'],
            target=sankey_data['link']['target'],
            value=sankey_data['link']['value']
        )
    ))
    
    # Update layout and show figure
    fig.update_layout(title_text="Sankey Diagram", font_size=st.session_state.font_size)

    # output the figure to streamlit
    st.plotly_chart(fig, use_container_width=True)



def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(page_title="Generate sankey for Milou!")
    st.title("Generate sankey!")
    display_sidebar_ui()

    st.session_state.sankey_data = pd.DataFrame()

    file_uploaded = st.file_uploader('Upload csv', type=['csv'], accept_multiple_files=False)
    if file_uploaded is not None:
        st.write("Found columns: ")
        df = pd.read_csv(file_uploaded)
        for col in df.columns:
            st.write(col)
        # Initialize empty dataframe to store all news
        st.session_state.sankey_data = df


    if not st.session_state.sankey_data.empty:
        # show button to generate sankey
        if st.button("Generate sankey"):
            generate_sankey(st.session_state.sankey_data)


if __name__ == "__main__":
    main()
