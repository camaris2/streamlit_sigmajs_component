import json
import streamlit as st
from vsigma_component import vsigma_component

st.set_page_config(
    layout = 'wide',
    page_title = 'Network Viz'
)

def filter_atttributes(d):
  # filter out some system attributes
  return {k:v for k,v in d.items() if k not in ['x', 'y', 'type', 'size', 'color', 'image', 'hidden', 'forceLabel', 'zIndex']} # , 'label']}

list_nodes_html = '--'
def list_nodes(state):
    data = graph_state["state"].get('lastselectedNodeData', {})
    print('data: ', data)
    print('nodes: ', my_nodes)
    list_nodes_html = ', '.join([n['key'] for n in my_nodes if n['attributes']['otype']==data['otype']])
    print('res:', list_nodes_html)
    return list_nodes_html

list_edges_html = '--'
def list_edges(state):
    data = graph_state["state"].get('lastselectedEdgeData', {})
    list_edges_html = ', '.join([n['key'] for n in my_edges if n['attributes']['otype']==data['otype']])
    return list_edges_html

# hold the VSigma internal state data
graph_state = {}

# Example nodes
my_nodes = [
      {
        "key": "Marie",
        "attributes": {
          "otype": "Person",
          "color": "red",
          "status": "active"
        }
      },
      {
        "key": "Gunther",
        "attributes": {
          "otype": "Person",
          "color": "blue",
          "status": "on pension"
        }
      },
      {
        "key": "Jake",
        "attributes": {
          "otype": "Person",
          "color": "black",
          "status": "deceased"
        }
      },
      {
        "key": "Lulu",
        "attributes": {
          "otype": "Animal",
          "color": "white",
          "status": "active"
        }
      }
    ]

# Example edges
my_edges = [
      {
        "key": "R001",
        "source": "Marie",
        "target": "Gunther",
        "attributes": {
          "otype": "Person-Person relation",
          "label": "Colleague"
        }
      },
      {
        "key": "R002",
        "source": "Marie",
        "target": "Jake",
        "attributes": {
          "otype": "Person-Person relation",
          "label": "Colleague"
        }
      },
      {
        "key": "R003",
        "source": "Gunther",
        "target": "Jake",
        "attributes": {
          "otype": "Person-Person relation",
          "label": "Colleague"
        }
      },
      {
        "key": "R004",
        "source": "Marie",
        "target": "Lulu",
        "attributes": {
          "otype": "Person-Animal relation",
          "label": "Pet"
        }
      }
    ]

# Example Settings
my_settings = {
    # "defaultNodeOuterBorderColor": "rgb(236, 81, 72)",
    # "defaultEdgeColor": "grey",
    # "edgeHoverSizeRatio": 5,
}

# PAGE LAYOUT

st.subheader("VSigma Component Demo App")
st.markdown("This is a VSigma component. It is a simple component that displays graph network data. It is a good example of how to use the VSigma component.")
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

col_graph, col_details = st.columns([2,1], gap="small")

with col_graph:
    graph_state = vsigma_component(my_nodes, my_edges, my_settings, key="vsigma") # add key to avoid reinit

with col_details:
    with st.container():
      if graph_state:
          if 'state' in graph_state:
              if type(graph_state['state'].get('lastselectedNodeData','')) == dict:
                  table_div = ''.join([f'<tr><td class="mca_key">{k}</td><td class="mca_value">{v}</td></tr>' for k,v in graph_state['state'].get('lastselectedNodeData', '').items() if k not in ['x', 'y', 'type', 'size', 'color', 'image', 'hidden', 'forceLabel', 'zIndex']])
                  table_div = '<table>'+table_div+'</table>'
                  st.markdown(f'<div class="card"><p class="mca_node">{graph_state["state"].get("lastselectedNode","")} (node)<br></p><div class="container">{table_div}</p></div><div class="mca_value">Linked to: {", ".join(graph_state["state"].get("hoveredNeighbors","[]"))}</div></div>', unsafe_allow_html = True)
                  if st.button("List all", key="list_all"):
                      html = list_nodes(graph_state["state"])
                      st.markdown(f'<div class="mca_value">{html}</div>', unsafe_allow_html = True)
              if type(graph_state['state'].get('lastselectedEdgeData','')) == dict:
                  table_div = ''.join([f'<tr><td class="mca_key">{k}</td><td class="mca_value">{v}</td></tr>' for k,v in graph_state['state'].get('lastselectedEdgeData', '').items() if k not in ['x', 'y', 'type', 'size', 'color', 'image', 'hidden', 'forceLabel', 'zIndex']])
                  table_div = '<table>'+table_div+'</table>'
                  st.markdown(f'<div class="card"><p class="mca_node">{graph_state["state"].get("lastselectedEdge","")} (edge)<br></p><div class="container">{table_div}</p></div></div>', unsafe_allow_html = True)
                  if st.button("List all", key="list_all"):
                      html = list_edges(graph_state["state"])
                      st.markdown(f'<div class="mca_value">{html}</div>', unsafe_allow_html = True)

with st.expander("Details graph state (debug)"):
    st.write(f'Type: {str(type(graph_state))}')
    st.write(graph_state)
