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

# Streamlit App Settings

st.set_page_config(
    layout = 'wide',
    page_title = 'Network Viz'
)

# State Variables

ss = st.session_state
ss.sigmaid = 0
ss.hidden_attributes = ['x', 'y', 'type', 'size', 'color', 'image', 'hidden', 'forceLabel', 'zIndex', 'index']

# Variables

graph_state = {} # holds the VSigma internal state data

# Helper Functions

list_nodes_html = '--'
def list_nodes(state):
    data = graph_state["state"].get('lastselectedNodeData', {})
    list_nodes_html = ', '.join([n['key'] for n in my_nodes if n['attributes']['nodetype']==data['nodetype']])
    return list_nodes_html
list_edges_html = '--'
def list_edges(state):
    data = graph_state["state"].get('lastselectedEdgeData', {})
    list_edges_html = ', '.join([n['key'] for n in my_edges if n['attributes']['edgetype']==data['edgetype']])
    return list_edges_html

# Load local or test data

# TODO: cache, load only once
if localdata:
    my_nodes = testdata['nodes']
    kind_of_nodes_filters=testdata['node_filters']
    my_edges = testdata['edges']
    kind_of_edges_filters=testdata['edge_filters']
    my_settings = testdata['settings']
elif testdata:
    my_nodes = testdata['nodes']
    kind_of_nodes_filters=testdata['node_filters']
    my_edges = testdata['edges']
    kind_of_edges_filters=testdata['edge_filters']
    my_settings = testdata['settings']

# Customize nodes and edges features based on their type (or other attributes)
# TODO: from config file ?

# TODO: cache, calculate only once
for node in my_nodes:
    kind = node['attributes']['nodetype']
    if kind == 'A':
        node['color'] = 'red'
        node['size'] = 5
        node['image'] = 'https://cdn.iconscout.com/icon/free/png-256/atom-1738376-1470282.png'
        node['label'] = node.get('label', node['key'])

for edge in my_edges:
    kind = edge['attributes']['edgetype']
    if kind == 'A':
        edge['color'] = 'red'
        edge['size'] = 1
        edge['type'] = edge.get('type', 'arrow') # arrow, line
        edge['label'] = edge.get('label', edge['key'])

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
      ss.edge_filters = col_efilters.multiselect("Edge filters:", options=kind_of_edges_filters, default=kind_of_edges_filters, key="edgefilters")
      ss.node_filters = col_nfilters.multiselect("Node filters (be carefull for inconsistency with edge filter):", options=kind_of_nodes_filters, default=kind_of_nodes_filters, key="nodefilters")
      ss.sigmaid = len(ss.node_filters)*100 + len(ss.edge_filters)
      if ss.sigmaid > 0:
        my_filtered_nodes = [n for n in my_nodes if n['attributes']['nodetype'] in ss.node_filters]
        my_filtered_edges = [e for e in my_edges if e['attributes']['edgetype'] in ss.edge_filters]
      else:
          my_filtered_nodes = my_nodes
          my_filtered_edges = my_edges
  else:
      my_filtered_nodes = my_nodes
      my_filtered_edges = my_edges
      ss.sigmaid = 0

# Graph and details
col_graph, col_details = st.columns([2,1], gap="small")

with col_graph:
    graph_state = vsigma_component(my_filtered_nodes, my_filtered_edges, my_settings, key="vsigma"+str(ss.sigmaid)) # add key to avoid reinit

with col_details:
    with st.container():
      if graph_state:
          if 'state' in graph_state:
              if type(graph_state['state'].get('lastselectedNodeData','')) == dict:
                  table_div = ''.join([
                      f'<tr><td class="mca_key">{k}</td><td class="mca_value">{v}</td></tr>'
                      for k,v in graph_state['state'].get('lastselectedNodeData', '').items()
                      if k not in ss.hidden_attributes
                ])
                  table_div = '<table>'+table_div+'</table>'
                  st.markdown(f'''
                      <div class="card">
                        <p class="mca_node">{graph_state["state"].get("lastselectedNode","")} (node)<br></p>
                        <div class="container">{table_div}</div>
                        <div class="mca_value">Linked to: {", ".join(graph_state["state"].get("hoveredNeighbors","[]"))}</div>
                      </div>
                      ''', unsafe_allow_html = True
                  )
              if type(graph_state['state'].get('lastselectedEdgeData','')) == dict:
                  table_div = ''.join([
                      f'<tr><td class="mca_key">{k}</td><td class="mca_value">{v}</td></tr>'
                      for k,v in graph_state['state'].get('lastselectedEdgeData', '').items()
                      if k not in ss.hidden_attributes
                  ])
                  table_div = '<table>'+table_div+'</table>'
                  st.markdown(f'''
                      <div class="card">
                        <p class="mca_node">{graph_state["state"].get("lastselectedEdge","")} (edge)<br></p>
                        <div class="container">{table_div}</div>
                      </div>
                      ''', unsafe_allow_html = True
                  )

if 'state' in graph_state:
    if type(graph_state['state'].get('lastselectedNodeData','')) == dict:
        if st.button("List all nodes of this type.", key="list_all"):
            html = list_nodes(graph_state["state"])
            st.markdown(f'<div class="mca_value">{html}</div><br>', unsafe_allow_html = True)
    if type(graph_state['state'].get('lastselectedEdgeData','')) == dict:
        if st.button("List all edges of this type.", key="list_all"):
            html = list_edges(graph_state["state"])
            st.markdown(f'<div class="mca_value">{html}</div><br>', unsafe_allow_html = True)

# Debug information

if DEBUG:
  with st.expander("Details graph state (debug)"):
      st.write(f"vsigma id: {ss.sigmaid}")
      st.write(f'Type: {str(type(graph_state))}')
      st.write(graph_state)