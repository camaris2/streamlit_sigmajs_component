import json
import streamlit as st
from vsigma_component import vsigma_component

# Test or local data imports

try:
    from test_data import testdata
except:
    testdata = None
try:
    from local_data import localdata
except:
    localdata = None

# Default settings

DEBUG = False
ENABLE_FILTERS = True
EXPERIMENTAL_FLAG = False  # Enable experimental features

# Streamlit App Settings

st.set_page_config(
    layout = 'wide',
    page_title = 'Network Viz'
)

# State Variables

ss = st.session_state
ss.sigmaid = 0
ss.hidden_attributes = ['x', 'y', 'type', 'size', 'color', 'image', 'hidden', 'forceLabel', 'zIndex', 'index']
if 'draw_count' not in ss:
    ss.draw_count = 0

ss.graph_state = {} # holds the VSigma internal state data

# Helper Functions

list_nodes_html = '--'
def list_nodes(state):
    data = ss.graph_state["state"].get('lastselectedNodeData', {})
    list_nodes_html = ', '.join([n['key'] for n in ss.my_nodes if n['attributes']['nodetype']==data['nodetype']])
    return list_nodes_html
list_edges_html = '--'
def list_edges(state):
    data = ss.graph_state["state"].get('lastselectedEdgeData', {})
    list_edges_html = ', '.join([n['key'] for n in ss.my_edges if n['attributes']['edgetype']==data['edgetype']])
    return list_edges_html

# Load local or test data
def load_data():
    if localdata:
        ss.my_nodes = [n for n in localdata['nodes']]
        ss.kind_of_nodes_filters = localdata['node_filters']
        ss.my_edges = [e for e in localdata['edges']]
        ss.kind_of_edges_filters = localdata['edge_filters']
        ss.my_settings = localdata['settings']

        if DEBUG:
            st.write("Local data:")
            st.write(localdata['nodes'])
            st.write("Local data loaded.")
            st.write(ss.my_nodes)


    elif testdata:
        ss.my_nodes = [n for n in testdata['nodes']]
        ss.kind_of_nodes_filters = testdata['node_filters']
        ss.my_edges = [e for e in testdata['edges']]
        ss.kind_of_edges_filters = testdata['edge_filters']
        ss.my_settings = testdata['settings']

        if DEBUG:
            st.write("Test data:")
            st.write(testdata['nodes'])
            st.write("Test data loaded.")
            st.write(ss.my_nodes)
    
    ss.my_filtered_nodes = ss.my_nodes
    ss.my_filtered_edges = ss.my_edges

# Customize nodes and edges features based on their type (or other attributes)
# TODO: from config file ?
# TODO: cache, calculate only once
def customize_nodes_edges():
    for node in ss.my_nodes:
        kind = node['attributes']['nodetype']
        if kind == 'A':
            node['color'] = 'red'
            node['size'] = 5
            node['image'] = 'https://cdn.iconscout.com/icon/free/png-256/atom-1738376-1470282.png'
            node['label'] = node.get('label', node['key'])

    for edge in ss.my_edges:
        kind = edge['attributes']['edgetype']
        if kind == 'A':
            edge['color'] = 'red'
            edge['size'] = 1
            edge['type'] = edge.get('type', 'arrow') # arrow, line
            edge['label'] = edge.get('label', edge['key'])

if 'my_nodes' not in ss or 'my_edges' not in ss:
    load_data()

# ss.my_filtered_nodes = ss.my_nodes
# ss.my_filtered_edges = ss.my_edges

# PAGE LAYOUT

st.subheader("VSigma Component Demo App")
st.markdown("This is a VSigma component. It is a simple component that displays graph network data. It is a good example of how to use the VSigma component.")
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

# Graph and Customize

if EXPERIMENTAL_FLAG:
    tab_graph, tab_customize, tab_experimental = st.tabs(["Graph", "Customize", "Experimental Features"])
else:
    tab_graph, tab_customize = st.tabs(["Graph", "Customize"])

if EXPERIMENTAL_FLAG:
    with tab_experimental:

        # Experimental features

        if EXPERIMENTAL_FLAG:
            st.markdown("### Experimental features")
            st.markdown("These features are experimental and may not work as expected.")
            st.markdown("They are not enabled by default, you can enable them in the code.")

            st.button("Add data", key="add_data")
            st.button("Reset data", key="reset_data")
            if st.session_state.get("reset_data", False):
                ss.my_nodes = None
                ss.kind_of_nodes_filters = None
                ss.my_edges = None
                ss.kind_of_edges_filters = None
                ss.my_settings = None

                ss.sigmaid += 1

                st.write("Data has been reset. Reloading data...")

                load_data()
                customize_nodes_edges()

            if st.session_state.get("add_data", False):
                # st.session_state.add_data = False
                new_node = {
                    "key": "N005",
                    "attributes": {
                        "nodetype": "Person",
                        "label": "New Node",
                        "color": "blue"
                    }
                }
                new_edge = {
                    "key": "R005",
                    "source": "N001",
                    "target": "N005",
                    "attributes": {
                        "edgetype": "Person-Person",
                        "label": "New Edge"
                    }
                }
                ss.my_nodes.append(new_node)
                ss.my_edges.append(new_edge)
                customize_nodes_edges()
                # # Re-render the component with the new data
                ss.sigmaid += 1
                # ss.graph_state, ss.sigma_component = vsigma_component(ss.my_nodes, ss.my_edges, ss.my_settings, key="vsigma"+str(ss.sigmaid))
                # ss.sigma_component.refresh()
                # st.write(ss.sigma_component.__dict__)
                # st.write(type(ss.sigma_component))

                st.write("Data was added. Reloading data...")

with tab_customize:

    left_col, center_col, right_col = st.columns([1,4,1], gap="small")

    with center_col:

        if ENABLE_FILTERS:
            st.write("Filter settings:")
            # TODO: handle consistency and remove unlinked nodes
            filters_flag = st.toggle("Use Filters", False)
            if filters_flag:
                # ss.edge_filters = st.pills("Edge filters:", options=kind_of_edges_filters, default=kind_of_edges_filters, key="edgefilters", selection_mode="multi")
                # ss.node_filters = st.pills("Node filters (be carefull for inconsistency with edge filter):", options=kind_of_nodes_filters, default=kind_of_nodes_filters, key="nodefilters", selection_mode="multi")
                ss.edge_filters = st.multiselect("Edge filters:", options=ss.kind_of_edges_filters, default=ss.kind_of_edges_filters, key="edgefilters")
                ss.node_filters = st.multiselect("Node filters (be carefull for inconsistency with edge filter):", options=ss.kind_of_nodes_filters, default=ss.kind_of_nodes_filters, key="nodefilters")
                ss.sigmaid = len(ss.node_filters)*100 + len(ss.edge_filters)
                if ss.sigmaid > 0:
                    ss.my_filtered_nodes = [n for n in ss.my_nodes if n['attributes']['nodetype'] in ss.node_filters]
                    ss.my_filtered_edges = [e for e in ss.my_edges if e['attributes']['edgetype'] in ss.edge_filters]
                else:
                    ss.my_filtered_nodes = ss.my_nodes
                    ss.my_filtered_edges = ss.my_edges
        else:
            ss.my_filtered_nodes = ss.my_nodes
            ss.my_filtered_edges = ss.my_edges
            ss.sigmaid = 0

        if DEBUG:
            st.write("Enables Filters:")
            if 'edge_filters' in ss:
                st.write("Edge filters:", ", ".join(ss.edge_filters))
            else:
                st.write("Edge filters: None")
            if 'node_filters' in ss:
                st.write("Node filters:", ", ".join(ss.node_filters))
            else:
                st.write("Node filters: None")

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
                    cs_split = setting.split(".")
                    if len(cs_split)==3:
                        cs_list.append(cs_split)
                st.write(cs_list)

with tab_graph:

    # Graph and details
    col_graph, col_details = st.columns([3,1], gap="small")

    with col_graph:
        ss.draw_count += 1
        if DEBUG: st.markdown(f"Draw count: {ss.draw_count}")
        ss.graph_state, ss.sigma_component = vsigma_component(ss.my_filtered_nodes, ss.my_filtered_edges, ss.my_settings, key="vsigma"+str(ss.sigmaid)) # add key to avoid reinit

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
                if 'hidden_attributes' in ss:
                    st.write("Hidden attributes:", ", ".join(ss.hidden_attributes))

if 'state' in ss.graph_state:
    if type(ss.graph_state['state'].get('lastselectedNodeData','')) == dict:
        if st.button("List all nodes of this type.", key="list_all"):
            html = list_nodes(ss.graph_state["state"])
            st.markdown(f'<div class="mca_value">{html}</div><br>', unsafe_allow_html = True)
    if type(ss.graph_state['state'].get('lastselectedEdgeData','')) == dict:
        if st.button("List all edges of this type.", key="list_all"):
            html = list_edges(ss.graph_state["state"])
            st.markdown(f'<div class="mca_value">{html}</div><br>', unsafe_allow_html = True)

# Debug information

if DEBUG:
    st.write("---")
    st.write(f"sigmaid: {ss.sigmaid}")
    with st.expander("Details graph state (debug)"):
        st.write(f"vsigma id: {ss.sigmaid}")
        st.write(f'Type: {str(type(ss.graph_state))}')
        st.write(ss.graph_state)
    with st.expander("Details graph data"):
        st.write(testdata)
