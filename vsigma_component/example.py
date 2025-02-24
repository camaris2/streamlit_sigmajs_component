import json
import streamlit as st
from vsigma_component import vsigma_component

ss = st.session_state
st.set_page_config(
    layout = 'wide',
    page_title = 'Network Viz'
)

ss.hidden_attributes = ['x', 'y', 'type', 'size', 'color', 'image', 'hidden', 'forceLabel', 'zIndex', 'index']

list_nodes_html = '--'
def list_nodes(state):
    data = graph_state["state"].get('lastselectedNodeData', {})
    print('data: ', data)
    print('nodes: ', my_nodes)
    list_nodes_html = ', '.join([n['key'] for n in my_nodes if n['attributes']['nodetype']==data['nodetype']])
    print('res:', list_nodes_html)
    return list_nodes_html

list_edges_html = '--'
def list_edges(state):
    data = graph_state["state"].get('lastselectedEdgeData', {})
    list_edges_html = ', '.join([n['key'] for n in my_edges if n['attributes']['edgetype']==data['edgetype']])
    return list_edges_html

# hold the VSigma internal state data
graph_state = {}

# Example nodes
my_nodes = [
      {
        "key": "N001",
        "attributes": {
          "nodetype": "Person",
          "label": "Marie",
          "color": "red",
          "status": "active",
          "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
        }
      },
      {
        "key": "N002",
        "attributes": {
          "nodetype": "Person",
          "label": "Gunther",
          "color": "blue",
          "status": "on pension",
          "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
        }
      },
      {
        "key": "N003",
        "attributes": {
          "nodetype": "Person",
          "label": "Jake",
          "color": "black",
          "status": "deceased",
          "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
        }
      },
      {
        "key": "N004",
        "attributes": {
          "nodetype": "Animal",
          "label": "Lulu",
          "color": "gray",
          "status": "active",
          "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
        }
      }
    ]

# Example edges
my_edges = [
      {
        "key": "R001",
        "source": "N001",
        "target": "N002",
        "attributes": {
          "edgetype": "Person-Person",
          "label": "Colleague",
        }
      },
      {
        "key": "R002",
        "source": "N001",
        "target": "N003",
        "attributes": {
          "edgetype": "Person-Person",
          "label": "Colleague",
        }
      },
      {
        "key": "R003",
        "source": "N002",
        "target": "N003",
        "attributes": {
          "edgetype": "Person-Person",
          "label": "Colleague",
        }
      },
      {
        "key": "R004",
        "source": "N001",
        "target": "N004",
        "attributes": {
          "edgetype": "Person-Animal",
          "label": "Pet",
        }
      }
    ]

# Example Settings
my_settings = {
    # labelFont, labelSize, labelWeight, labelColor
    # edgeLabelFont, edgeLabelSize, edgeLabelWeight, edgeLabelColor

    # "defaultNodeOuterBorderColor": "rgb(236, 81, 72)",
    # "defaultEdgeColor": "grey",
    # "edgeHoverSizeRatio": 5,
}

# PAGE LAYOUT

st.subheader("VSigma Component Demo App")
st.markdown("This is a VSigma component. It is a simple component that displays graph network data. It is a good example of how to use the VSigma component.")
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

ss.sigmaid = 0
filters_flag = st.toggle("Use Filters", False)

col_efilters, col_nfilters = st.columns([1,1], gap="small")
if filters_flag:
    ss.edge_filters = col_efilters.pills("Edge filters:", options=["Person-Person", "Person-Animal"], default=["Person-Person", "Person-Animal"], key="edgepills", selection_mode="multi")
    ss.node_filters = col_nfilters.pills("Node filters (be carefull for inconsistency with edge filter):", options=["Person", "Animal"], default=["Person", "Animal"], key="nodepills", selection_mode="multi")
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

col_graph, col_details = st.columns([2,1], gap="small")

with col_graph:
    graph_state = vsigma_component(my_filtered_nodes, my_filtered_edges, my_settings, key="vsigma"+str(ss.sigmaid)) # add key to avoid reinit

with col_details:
    with st.container():
      if graph_state:
          if 'state' in graph_state:
              if type(graph_state['state'].get('lastselectedNodeData','')) == dict:
                  table_div = ''.join([f'<tr><td class="mca_key">{k}</td><td class="mca_value">{v}</td></tr>' for k,v in graph_state['state'].get('lastselectedNodeData', '').items() if k not in ss.hidden_attributes])
                  table_div = '<table>'+table_div+'</table>'
                  st.markdown(f'<div class="card"><p class="mca_node">{graph_state["state"].get("lastselectedNode","")} (node)<br></p><div class="container">{table_div}</p></div><div class="mca_value">Linked to: {", ".join(graph_state["state"].get("hoveredNeighbors","[]"))}</div></div>', unsafe_allow_html = True)
              if type(graph_state['state'].get('lastselectedEdgeData','')) == dict:
                  table_div = ''.join([f'<tr><td class="mca_key">{k}</td><td class="mca_value">{v}</td></tr>' for k,v in graph_state['state'].get('lastselectedEdgeData', '').items() if k not in ss.hidden_attributes])
                  table_div = '<table>'+table_div+'</table>'
                  st.markdown(f'<div class="card"><p class="mca_node">{graph_state["state"].get("lastselectedEdge","")} (edge)<br></p><div class="container">{table_div}</p></div></div>', unsafe_allow_html = True)

if 'state' in graph_state:
    if type(graph_state['state'].get('lastselectedNodeData','')) == dict:
        if st.button("List all nodes of this type.", key="list_all"):
            html = list_nodes(graph_state["state"])
            st.markdown(f'<div class="mca_value">{html}</div><br>', unsafe_allow_html = True)
    if type(graph_state['state'].get('lastselectedEdgeData','')) == dict:
        if st.button("List all edges of this type.", key="list_all"):
            html = list_edges(graph_state["state"])
            st.markdown(f'<div class="mca_value">{html}</div><br>', unsafe_allow_html = True)


with st.expander("Details graph state (debug)"):
    st.write(f"vsigma id: {ss.sigmaid}")
    st.write(f'Type: {str(type(graph_state))}')
    st.write(graph_state)
