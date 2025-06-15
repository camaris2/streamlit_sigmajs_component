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

# Variables

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
        ss.my_nodes = localdata['nodes']
        ss.kind_of_nodes_filters = localdata['node_filters']
        ss.my_edges = localdata['edges']
        ss.kind_of_edges_filters = localdata['edge_filters']
        ss.my_settings = localdata['settings']
    elif testdata:
        ss.my_nodes = testdata['nodes']
        ss.kind_of_nodes_filters = testdata['node_filters']
        ss.my_edges = testdata['edges']
        ss.kind_of_edges_filters = testdata['edge_filters']
        ss.my_settings = testdata['settings']

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


# PAGE LAYOUT

st.subheader("VSigma Component Demo App")
st.markdown("This is a VSigma component. It is a simple component that displays graph network data. It is a good example of how to use the VSigma component.")
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

if ENABLE_FILTERS:
  # TODO: handle consistency and remove unlinked nodes
  filters_flag = st.toggle("Use Filters", False)
  col_efilters, col_nfilters = st.columns([1,1], gap="small")
  if filters_flag:
      # ss.edge_filters = col_efilters.pills("Edge filters:", options=kind_of_edges_filters, default=kind_of_edges_filters, key="edgefilters", selection_mode="multi")
      # ss.node_filters = col_nfilters.pills("Node filters (be carefull for inconsistency with edge filter):", options=kind_of_nodes_filters, default=kind_of_nodes_filters, key="nodefilters", selection_mode="multi")
      ss.edge_filters = col_efilters.multiselect("Edge filters:", options=ss.kind_of_edges_filters, default=ss.kind_of_edges_filters, key="edgefilters")
      ss.node_filters = col_nfilters.multiselect("Node filters (be carefull for inconsistency with edge filter):", options=ss.kind_of_nodes_filters, default=ss.kind_of_nodes_filters, key="nodefilters")
      ss.sigmaid = len(ss.node_filters)*100 + len(ss.edge_filters)
      if ss.sigmaid > 0:
        my_filtered_nodes = [n for n in ss.my_nodes if n['attributes']['nodetype'] in ss.node_filters]
        my_filtered_edges = [e for e in ss.my_edges if e['attributes']['edgetype'] in ss.edge_filters]
      else:
          my_filtered_nodes = ss.my_nodes
          my_filtered_edges = ss.my_edges
  else:
      my_filtered_nodes = ss.my_nodes
      my_filtered_edges = ss.my_edges
      ss.sigmaid = 0

# Graph and details
col_graph, col_details = st.columns([2,1], gap="small")

with col_graph:
    ss.draw_count += 1
    st.markdown(f"Draw count: {ss.draw_count}")
    ss.graph_state, ss.sigma_component = vsigma_component(my_filtered_nodes, my_filtered_edges, ss.my_settings, key="vsigma"+str(ss.sigmaid)) # add key to avoid reinit

with col_details:

    tab1, tab2, tab3 = st.tabs(["Details", "Filters", "Settings"])

    with tab1:

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
    with tab2:
        st.write("Filters:")
        if 'edge_filters' in ss:
            st.write("Edge filters:", ss.edge_filters)
        else:
            st.write("Edge filters: None")
        if 'node_filters' in ss:
            st.write("Node filters:", ss.node_filters)
        else:
            st.write("Node filters: None")
        if 'hidden_attributes' in ss:
            st.write("Hidden attributes:", ss.hidden_attributes)
        else:
            st.write("Hidden attributes: None")

    with tab3:
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

if 'state' in ss.graph_state:
    if type(ss.graph_state['state'].get('lastselectedNodeData','')) == dict:
        if st.button("List all nodes of this type.", key="list_all"):
            html = list_nodes(ss.graph_state["state"])
            st.markdown(f'<div class="mca_value">{html}</div><br>', unsafe_allow_html = True)
    if type(ss.graph_state['state'].get('lastselectedEdgeData','')) == dict:
        if st.button("List all edges of this type.", key="list_all"):
            html = list_edges(ss.graph_state["state"])
            st.markdown(f'<div class="mca_value">{html}</div><br>', unsafe_allow_html = True)

# Experimental features

if EXPERIMENTAL_FLAG:
    st.markdown("### Experimental features")
    st.markdown("These features are experimental and may not work as expected.")
    st.markdown("They are not enabled by default, you can enable them in the code.")

    st.button("Add data", key="add_data")
    if st.button("Reset data"):
        ss.my_nodes = None
        ss.kind_of_nodes_filters = None
        ss.my_edges = None
        ss.kind_of_edges_filters = None
        ss.my_settings = None

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
        st.write(ss.sigma_component.__dict__)
        st.write(type(ss.sigma_component))

# Debug information

if DEBUG:
    st.write(f"sigmaid: {ss.sigmaid}")
    with st.expander("Details graph state (debug)"):
        st.write(f"vsigma id: {ss.sigmaid}")
        st.write(f'Type: {str(type(ss.graph_state))}')
        st.write(ss.graph_state)
    with st.expander("Details graph data"):
        st.write(testdata)
