# data should contain following keys: 
# - node_filters: to enable filtering of nodes
# - nodes: list of nodes (must contain key and attributes.nodetype)
# - edge_filters: to enable filtering of edges
# - edges: list of edges (must contain source and target keys and attributes.edgetype)
# - settings:sigmajs v3.x settings for the graph

testdata = {
    'node_filters': ["Person", "Animal"],
    'nodes': [
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
    ],
    'edge_filters': ["Person-Person", "Person-Animal"],
    'edges': [
        {
            "key": "R001",
            "source": "N001",
            "target": "N002",
            "attributes": {
                "edgetype": "Person-Person",
                "label": "Friends",
                "status": "active",
                "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
            }
        },
        {
            "key": "R002",
            "source": "N001",
            "target": "N003",
            "attributes": {
                "edgetype": "Person-Person",
                "label": "Family",
                "status": "active",
                "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
            }
        },
        {
            "key": "R003",
            "source": "N002",
            "target": "N003",
            "attributes": {
                "edgetype": "Person-Person",
                "label": "Friends",
                "status": "active",
                "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
            }
        },
        {
            "key": "R004",
            "source": "N001",
            "target": "N004",
            "attributes": {
                "edgetype": "Person-Animal",
                "label": "Owner",
                "status": "active",
                "image": "https://icons.getbootstrap.com/assets/icons/person.svg",
            }
        }
    ],
    'settings': {
    }
}