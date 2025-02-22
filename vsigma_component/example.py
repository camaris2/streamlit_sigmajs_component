import json
import streamlit as st
from vsigma_component import vsigma_component

ss = st.session_state

st.set_page_config(
    layout = 'wide',
    page_title = 'Network Viz',
)

if not 'counter' in ss:
  ss.counter=1

def filter_atttributes(d):
  # filter out some system attributes
  return {k:v for k,v in d.items() if k not in ['x', 'y', 'size', 'color', 'hidden', 'forceLabel', 'zIndex']} # , 'label', 'image']}

list_nodes_html = '--'
def list_nodes(state):
    data = graph_state["state"].get('lastselectedNodeData', {})
    print('data: ', data)
    print('nodes: ', my_nodes)
    list_nodes_html = ', '.join([n['key'] for n in my_nodes if n['attributes']['type']==data['type']])
    print('res:', list_nodes_html)
    return list_nodes_html

list_edges_html = '--'
def list_edges(state):
    data = graph_state["state"].get('lastselectedEdgeData', {})
    list_edges_html = ', '.join([n['key'] for n in my_edges if n['attributes']['type']==data['type']])
    return list_edges_html

# hold the VSigma internal state data
graph_state = {}

# Example nodes
my_nodes = [
      {
        "key": "Marie",
        "attributes": {
          "type": "Person",
          "color": "red",
          "status": "active",
          "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
        }
      },
      {
        "key": "Gunther",
        "attributes": {
          "type": "Person",
          "color": "blue",
          "status": "on pension",
          "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
        }
      },
      {
        "key": "Jake",
        "attributes": {
          "type": "Person",
          "color": "black",
          "status": "deceased",
          "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
        }
      },
      {
        "key": "Lulu3",
        "attributes": {
          "type": "Animal",
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
        "source": "Marie",
        "target": "Gunther",
        "attributes": {
          "type": "Person-Person relation",
          "label": "Colleague",
        }
      },
      {
        "key": "R002",
        "source": "Marie",
        "target": "Jake",
        "attributes": {
          "type": "Person-Person relation",
          "label": "Colleague",
        }
      },
      {
        "key": "R003",
        "source": "Gunther",
        "target": "Jake",
        "attributes": {
          "type": "Person-Person relation",
          "label": "Colleague",
        }
      },
      {
        "key": "R004",
        "source": "Marie",
        "target": "Lulu3",
        "attributes": {
          "type": "Person-Animal relation",
          "label": "Pet",
        }
      }
    ]

# Node types
my_node_types = ["Person", "Animal"]

# Edge types
my_edge_types = ["Person-Person relation", "Person-Animal relation"]

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

ss.key = 'vsigma'+str(ss.counter)

with col_graph:
    col_filter_nodes, col_filter_edges = st.columns([1,1])
    all_nodes_filter = my_node_types
    all_edges_filter = my_edge_types
    with col_filter_nodes:
      ss.nodes_filter = st.multiselect(
        "Filter nodes",
        all_nodes_filter,
        all_nodes_filter,
      )
      st.write("You selected:", ', '.join(ss.nodes_filter))
    with col_filter_edges:
      ss.edges_filter = st.multiselect(
        "Filter nodes",
        all_edges_filter,
        all_edges_filter
      )
    if not 'selected_nodes_filter' in ss:
      ss.selected_nodes_filter = all_nodes_filter
    else:
      ss.selected_nodes_filter = ss.nodes_filter
    if not 'selected_edges_filter' in ss:
      ss.selected_edges_filter = all_edges_filter
    else:
      ss.selected_edges_filter = ss.edges_filter
      st.write("You selected:", ', '.join(ss.edges_filter))
    # Filtering
    my_nodes = [n for n in my_nodes if n['attributes']['type'] in ss.nodes_filter]
    my_edges = [e for e in my_edges if e['attributes']['type'] in ss.edges_filter]
    if not (ss.nodes_filter == ss.selected_nodes_filter and ss.edges_filter == ss.selected_edges_filter):
      ss.counter += 1
    ss.key = 'vsigma'+str(ss.counter)
    # st.write(f'Nodes: {my_nodes}')
    # st.write(f'Edges: {my_edges}')
    graph_state = vsigma_component(my_nodes, my_edges, my_settings, key=ss.key)

with col_details:
    with st.container():
      if graph_state:
          if 'state' in graph_state:
              if type(graph_state['state'].get('lastselectedNodeData','')) == dict:
                  table_div = ''.join([f'<tr><td class="mca_key">{k}</td><td class="mca_value">{v}</td></tr>' for k,v in graph_state['state'].get('lastselectedNodeData', '').items() if k not in ['x', 'y', 'type', 'size', 'color', 'image', 'hidden', 'forceLabel', 'zIndex']])
                  table_div = '<table>'+table_div+'</table>'
                  if len(graph_state["state"].get("hoveredNeighbors",[])) > 0:
                    linked_html = f"Linked to: {', '.join(graph_state['state'].get('hoveredNeighbors',[]))}"
                  else:
                    linked_html = ""
                  st.markdown(f'<div class="card"><p class="mca_node">{graph_state["state"].get("lastselectedNode","")} (node)<br></p><div class="container">{table_div}</p></div><div class="mca_value">{linked_html}</div></div>', unsafe_allow_html = True)
                  st.markdown(f'<br/>', unsafe_allow_html = True)
                  if st.button("List all nodes of same type", key="list_all"):
                      html = list_nodes(graph_state["state"])
                      st.markdown(f'<div class="mca_value">{html}</div>', unsafe_allow_html = True)
              if type(graph_state['state'].get('lastselectedEdgeData','')) == dict:
                  table_div = ''.join([f'<tr><td class="mca_key">{k}</td><td class="mca_value">{v}</td></tr>' for k,v in graph_state['state'].get('lastselectedEdgeData', '').items() if k not in ['x', 'y', 'type', 'size', 'color', 'image', 'hidden', 'forceLabel', 'zIndex']])
                  table_div = '<table>'+table_div+'</table>'
                  st.markdown(f'<div class="card"><p class="mca_node">{graph_state["state"].get("lastselectedEdge","")} (edge)<br></p><div class="container">{table_div}</p></div></div>', unsafe_allow_html = True)
                  st.markdown(f'<br/>', unsafe_allow_html = True)
                  if st.button("List all edges of same type", key="list_all"):
                      html = list_edges(graph_state["state"])
                      st.markdown(f'<div class="mca_value">{html}</div>', unsafe_allow_html = True)

with st.expander("Details graph state (debug)"):
    st.write(f'Type: {str(type(graph_state))}')
    st.write(graph_state)
    st.write(f'Graph key: {ss.key}')
