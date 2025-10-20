import random
import streamlit as st
from vsigma_component import vsigma_component
from tools import (
    list_nodes,
    list_edges,
    addNode,
    removeRandomNode,
    removeRandomEdge,
    load_or_reuse_data,
)


# Default settings

DEBUG = False
ENABLE_FILTERS = True
EXPERIMENTAL_FLAG = True  # Enable experimental features
PROFILE = False  # Enable profiling

import cProfile
import pstats
from io import StringIO
pr = cProfile.Profile()
if PROFILE:
    print("Start profiling...")
    pr.enable()

# Streamlit App Settings

st.set_page_config(
    layout = 'wide',
    page_title = 'Network Viz'
)

# State Variables

ss = st.session_state
if 'sigmaid' not in ss:
    ss.sigmaid = 0
if 'hidden_attributes' not in ss:
    ss.hidden_attributes = [
        # 'x', 'y',
        'type',
        'size', 'color', 'image',
        'label','hidden', 'forceLabel',
        'zIndex', 'index'
    ]

if 'draw_count' not in ss:
    ss.draw_count = 0

if "positions" not in ss:
    ss.positions = {}

if "node_filters" not in ss:
    if "kind_of_nodes_filters" in ss:
        ss.node_filters = ss.kind_of_nodes_filters
    else:
        ss.node_filters = []
if "edge_filters" not in ss:
    if "kind_of_edges_filters" in ss:
        ss.edge_filters = ss.kind_of_edges_filters
    else:
        ss.edge_filters = []

ss.graph_state = {} # holds the VSigma internal state data

load_or_reuse_data()

# PAGE LAYOUT

st.subheader("VSigma Component Demo App")
st.markdown("This is a VSigma component. It is a simple component that displays graph network data. It is a good example of how to use the VSigma component.")
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

# Graph and Customize

if EXPERIMENTAL_FLAG:
    tab_graph, tab_filters, tab_customize, tab_experimental = st.tabs(["Graph", "Filters", "Customize", "Experimental Features"])
else:
    tab_graph, tab_filters, tab_customize = st.tabs(["Graph", "Filters", "Customize"])

if EXPERIMENTAL_FLAG:
    with tab_experimental:

        # Experimental features

        if EXPERIMENTAL_FLAG:
            st.markdown("### Experimental features")
            st.markdown("These features are experimental and may not work as expected.")
            st.markdown("They are not enabled by default, you can enable them in the code.")

            if st.button("Add Node", key="add_node"):
                addNode()
                # Re-render the component with the new data
                ss.sigmaid += 1
                st.write("Nodes and edges were added. Reloading component ...")

            if st.button("Remove Random Node", key="remove_node"):
                removeRandomNode()
                # Re-render the component with the new data
                ss.sigmaid += 1
                st.write("Node was removed. Reloading component ...")

            if st.button("Remove Random Edge", key="remove_edge"):
                removeRandomEdge()
                # Re-render the component with the new data
                ss.sigmaid += 1
                st.write("Edge was removed. Reloading component ...")

            if st.button("Reset data", key="reset_data"):
                ss.my_nodes = None
                ss.kind_of_nodes_filters = None
                ss.my_edges = None
                ss.kind_of_edges_filters = None
                ss.my_settings = None

                # Re-render the component with the new data
                ss.sigmaid += 1
                st.write("Data was added. Reloading component ...")

                load_or_reuse_data(force=True)

with tab_filters:

    left_col, center_col, right_col = st.columns([1,4,1], gap="small")

    with center_col:

        if ENABLE_FILTERS:
            # TODO: handle consistency and remove unlinked nodes
            filters_flag = st.toggle("Use Filters", False)
            if filters_flag:
                # ss.edge_filters = st.pills("Edge filters:", options=kind_of_edges_filters, default=kind_of_edges_filters, key="edgefilters", selection_mode="multi")
                # ss.node_filters = st.pills("Node filters (be carefull for inconsistency with edge filter):", options=kind_of_nodes_filters, default=kind_of_nodes_filters, key="nodefilters", selection_mode="multi")
                ss.edge_filters = st.multiselect("Edge filters:", options=ss.kind_of_edges_filters, default=ss.kind_of_edges_filters, key="edgefilters")
                ss.node_filters = st.multiselect("Node filters (be carefull for inconsistency with edge filter):", options=ss.kind_of_nodes_filters, default=ss.kind_of_nodes_filters, key="nodefilters")
                # ss.sigmaid = len(ss.node_filters)*100 + len(ss.edge_filters)
                ss.my_filtered_nodes = [n for n in ss.my_nodes if n['attributes']['nodetype'] in ss.node_filters]
                ss.my_filtered_edges = [e for e in ss.my_edges if e['attributes']['edgetype'] in ss.edge_filters]

                if st.button("update graph"):
                    ss.sigmaid += 1
                    st.write(f"sigmaid updated to {ss.sigmaid}")

        else:
            ss.my_filtered_nodes = ss.my_nodes
            ss.my_filtered_edges = ss.my_edges

        if DEBUG:
            st.write("Enabled Filters:")
            if 'edge_filters' in ss:
                st.write("Edge filters:", ", ".join(ss.edge_filters))
            else:
                st.write("Edge filters: None")
            if 'node_filters' in ss:
                st.write("Node filters:", ", ".join(ss.node_filters))
            else:
                st.write("Node filters: None")

with tab_customize:

    cust_left_col, cust_center_col, cust_right_col = st.columns([1,4,1], gap="small")

    with cust_center_col:

        st.write("Base settings:")
        st.write(ss.my_settings)
        if EXPERIMENTAL_FLAG:
            st.write("Custom settings:")
            custom_settings = st.text_area(
                "Custom Settings", 
                value="", 
                height=None, 
                max_chars=None, 
                key=None, 
                help=None, 
                on_change=None, 
                args=None, 
                kwargs=None, 
                placeholder=None, 
                disabled=False, 
                label_visibility="collapsed"
            )
            if custom_settings:
                cs = custom_settings.split('\\n')
                cs = [s.strip() for s in cs]
                cs_list = []
                for setting in cs:
                    cs_split = setting.split(":")
                    if len(cs_split)>1:
                        cs_list.append(cs_split)
                st.write(cs_list)

with tab_graph:

    # Graph and details
    col_graph, col_details = st.columns([3,1], gap="small")

    with col_graph:
        ss.draw_count += 1
        if DEBUG: st.markdown(f"Draw count: {ss.draw_count} - sigmaid: {ss.sigmaid}")
        ss.graph_state, ss.sigma_component = vsigma_component(ss.my_filtered_nodes, ss.my_filtered_edges, ss.my_settings, positions=ss.positions, key="vsigma"+str(ss.sigmaid)) # add key to avoid reinit

    with col_details:

        if ss.graph_state:
            if 'state' in ss.graph_state:
                data = {}
                label = ""
                gtype = ""
                if type(ss.graph_state['state'].get('lastselectedNodeData','')) == dict:
                    data ={k:v for k,v in ss.graph_state['state'].get('lastselectedNodeData', '').items() if k not in ss.hidden_attributes}
                    label = ss.graph_state["state"].get("lastselectedNode","")
                    gtype = "node"
                if type(ss.graph_state['state'].get('lastselectedEdgeData','')) == dict:
                    data ={k:v for k,v in ss.graph_state['state'].get('lastselectedEdgeData', '').items() if k not in ss.hidden_attributes}
                    label = ss.graph_state["state"].get("lastselectedEdge","")
                    gtype = "edge"

                table_div = ''.join([
                    f'<tr><td class="mca_key">{k}</td><td class="mca_value">{v}</td></tr>'
                    for k,v in data.items()
                ])
                table_div = '<table>'+table_div+'</table>'
                if len(gtype) > 0:
                    st.markdown(f'''
                        <div class="card">
                        <p class="mca_node">{label} ({gtype})<br></p>
                        <div class="container">{table_div}</div>
                        </div>
                        ''', unsafe_allow_html = True
                    )
                if DEBUG:
                    if 'hidden_attributes' in ss:
                        st.write("Hidden attributes:", ", ".join(ss.hidden_attributes))

if 'state' in ss.graph_state:
    if type(ss.graph_state['state'].get('lastselectedNodeData','')) == dict:
        if st.button("List all nodes of this type.", key="list_all"):
            html = list_nodes(ss.graph_state["state"])
            st.markdown(f'<div class="mca_value">{"<br>".join(html)}</div><br>', unsafe_allow_html = True)
    if type(ss.graph_state['state'].get('lastselectedEdgeData','')) == dict:
        if st.button("List all edges of this type.", key="list_all"):
            html = list_edges(ss.graph_state["state"])
            st.markdown(f'<div class="mca_value">{"<br>".join(html)}</div><br>', unsafe_allow_html = True)
    if 'positions' in ss.graph_state['state']:
        if len(ss.graph_state['state']['positions'])>0:
            ss.positions = ss.graph_state['state']['positions']

# Debug information

if DEBUG:

    if st.button("update sigma id to refresh component"):
        ss.sigmaid += 1
        st.write(f"sigmaid updated to {ss.sigmaid}")

    if st.button("Test positioning"):
        # ss.positions = ss.graph_state["state"].get("positions", {})
        for pos in ss.positions.values():
            pos['x'] = pos.get('x', 0) + random.random() * 5.0 - 2.5
            pos['y'] = pos.get('y', 0) + random.random() * 5.0 - 2.5
        st.write("Added random jitter to positions...")
        st.write(ss.positions.values()[:3])
        st.write("...")

    st.write("---")
    st.write(f"sigmaid: {ss.sigmaid}")
    with st.expander("Details graph state (debug)"):
        st.write(f"vsigma id: {ss.sigmaid}")
        st.write(ss.graph_state)
    with st.expander("Details actual graph data"):
        st.write("Positions:")
        st.write(ss.positions)
        st.write("Nodes:")
        st.write(ss.my_nodes)
        st.write("Edges:")
        st.write(ss.my_edges)
        st.write("Settings:")
        st.write(ss.my_settings)
        st.write("Filtered Nodes:")
        st.write(ss.my_filtered_nodes)
        st.write("Filtered Edges:")
        st.write(ss.my_filtered_edges)

if PROFILE:
    pr.disable()
    s = StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10)
    print(s.getvalue())
    with st.expander("Profiling info"):
        st.text(s.getvalue())
    print("Ended profiling.")
