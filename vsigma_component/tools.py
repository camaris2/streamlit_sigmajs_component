import random
import streamlit as st

# Helper Functions

list_nodes_html = '--'
def list_nodes(state):
    data = st.session_state.graph_state["state"].get('lastselectedNodeData', {})
    list_nodes_html = [
        n['key'] + ' : ' + ', '.join(
            [att + '=' + n['attributes'][att] for att in n['attributes']]
        )
        for n in st.session_state.my_nodes if n['attributes']['nodetype']==data['nodetype']
    ]
    return list_nodes_html

list_edges_html = '--'
def list_edges(state):
    data = st.session_state.graph_state["state"].get('lastselectedEdgeData', {})
    list_edges_html = [
        n['key'] + ' : ' + ', '.join(
            [att + '=' + n['attributes'][att] for att in n['attributes']]
        )
        for n in st.session_state.my_edges if n['attributes']['edgetype']==data['edgetype']
    ]
    return list_edges_html

# Customize nodes and edges features based on their type (or other attributes)

def customize_node(node):
    kind = node['attributes']['nodetype']
    if kind == 'A':
        node['color'] = 'red'
        node['size'] = 5
        node['image'] = 'https://cdn.iconscout.com/icon/free/png-256/atom-1738376-1470282.png'
        node['label'] = node.get('label', node['key'])

    return node

def customize_edge(edge):
    kind = edge['attributes']['edgetype']
    if kind == 'A':
        edge['color'] = 'red'
        edge['size'] = 1
        edge['type'] = edge.get('type', 'arrow') # arrow, line
        edge['label'] = edge.get('label', edge['key'])

    return edge

def customize_nodes_edges():
    for node in st.session_state.my_nodes:
        customize_node(node)
    for edge in st.session_state.my_edges:
        customize_edge(edge)

def addNode():
    nid = 'N' + str(len(st.session_state.my_nodes)+1).rjust(3, '0')
    eid = 'R' + str(len(st.session_state.my_edges)+1).rjust(3, '0')
    rnid = 'N' + str(1+int(len(st.session_state.my_nodes)*random.random())).rjust(3, '0')

    st.write(f"Add Node {nid}, connect to {rnid}")
    print(f"Add Node {nid}, connect to {rnid}")

    new_node = {
        "key": nid,
        "attributes": {
            "nodetype": "Person",
            "label": "New Person",
            "color": "blue",
            "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
        }
    }
    new_edge = {
        "key": eid,
        "source": rnid,
        "target": nid,
        "attributes": {
            "edgetype": "Person-Person",
            "label": "New Edge"
        }
    }

    new_node = customize_node(new_node)
    new_edge = customize_edge(new_edge)

    st.session_state.my_nodes.append(new_node)
    st.session_state.my_edges.append(new_edge)
    if st.session_state.node_filters: 
        if new_node['attributes']['nodetype'] in st.session_state.node_filters:
            st.session_state.my_filtered_nodes.append(new_node)
        if new_edge['attributes']['edgetype'] in st.session_state.edge_filters:
            st.session_state.my_filtered_edges.append(new_edge)
    st.session_state.positions[new_node['key']] = { "x": random.random(), "y": random.random() }

def removeRandomNode():
    if len(st.session_state.my_nodes) > 0:
        nid = random.choice(st.session_state.my_nodes)['key']
        st.write(f"Remove Node {nid} and its edges")
        print(f"Remove Node {nid} and its edges")
        st.session_state.my_nodes = [n for n in st.session_state.my_nodes if n['key'] != nid]
        st.session_state.my_filtered_nodes = [n for n in st.session_state.my_filtered_nodes if n['key'] != nid]
        st.session_state.my_edges = [e for e in st.session_state.my_edges if e['source'] != nid and e['target'] != nid]
        st.session_state.my_filtered_edges = [e for e in st.session_state.my_filtered_edges if e['source'] != nid and e['target'] != nid]
        if nid in st.session_state.positions:
            del st.session_state.positions[nid]

def removeRandomEdge():
    if len(st.session_state.my_edges) > 0:    
        eid = random.choice(st.session_state.my_edges)['key']
        st.write(f"Remove Edge {eid}")
        print(f"Remove Edge {eid}")
        st.session_state.my_edges = [e for e in st.session_state.my_edges if e['key'] != eid]
        st.session_state.my_filtered_edges = [e for e in st.session_state.my_filtered_edges if e['key'] != eid]

# LOAD DATA, 'local data' or fallback 'test data' imports, only run once
def load_or_reuse_data(force=False):
    if force or not('my_nodes' in st.session_state and 'my_edges' in st.session_state):
        data = None
        try:
            from local_data import localdata as data
        except:
            data = None
            try:
                from test_data import testdata as data
            except:
                data = None
        if data is None:
            st.session_state.my_nodes = [n for n in data['nodes']]
            st.session_state.kind_of_nodes_filters = data['node_filters']
            st.session_state.my_edges = [e for e in data['edges']]
            st.session_state.kind_of_edges_filters = data['edge_filters']
            st.session_state.my_settings = data['settings']
        else:
            st.session_state.my_nodes = [n for n in data['nodes']]
            st.session_state.kind_of_nodes_filters = data['node_filters']
            st.session_state.my_edges = [e for e in data['edges']]
            st.session_state.kind_of_edges_filters = data['edge_filters']
            st.session_state.my_settings = data['settings']
        
        for node in st.session_state.my_nodes:
            customize_node(node)
        for edge in st.session_state.my_edges:
            customize_edge(edge)

        st.session_state.my_filtered_nodes = st.session_state.my_nodes
        st.session_state.my_filtered_edges = st.session_state.my_edges
