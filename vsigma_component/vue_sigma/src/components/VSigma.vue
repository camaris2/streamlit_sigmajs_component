<template>
  <div class="graph">
    <div class="networkinfo">
      {{ state.nnodes }} Nodes - {{ state.nedges }} Edges
      <button id="sync2st">Save</button>
      <button id="refresh">⭮</button>
    </div>
    <div>
      <button id="start">arrange</button>
      <button id="stop">stop</button>
      <button id="reset">reset</button>&nbsp;
      <span id="search">
      <input type="search" id="search-input" list="suggestions" placeholder="Search node...">
      <datalist id="suggestions">
        <option value="Musk"></option>
        <option value="Gates"></option>
      </datalist>
    </span>
    </div>
    <div class="selected">{{ state.hoveredNode }} {{ state.hoveredNodeLabel }}{{ state.hoveredEdge }} {{ state.hoveredEdgeLabel }}&nbsp;</div>
    <div id="sigma-container"></div>
  </div>
</template>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 0px;
}
.graph {
  background-color: #fefefe;
  border: 1px solid #e8e8e8;
  padding: 5px;
}
.networkinfo {
  font-size: x-small;
  float: right;
}
.selected {
  float: right;
  font-size: x-small;
}
.debuginfo {
  display: block;
  visibility: hidden;
  background-color: coral;
  color: white;
  font-size: 10px;
}
#sigma-container {
  position: relative;
  height: 600px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
}
button + button {
  margin-left: 10px;
}
</style>

<script setup>
  import { NodePictogramProgram } from "@sigma/node-image";
  // import getNodePictogramProgram from "sigma/rendering/webgl/programs/node.image";
  import Graph from "graphology";
  import { circlepack } from "graphology-layout";
  import {collectLayout, assignLayout} from 'graphology-layout/utils';
  import FA2Layout from "graphology-layout-forceatlas2/worker";
  import ForceSupervisor from "graphology-layout-force/worker";
  import forceAtlas2 from "graphology-layout-forceatlas2";
  import Sigma from "sigma";
  import { onMounted, onUnmounted, reactive, ref, watch, computed } from "vue";
  import { Streamlit } from 'streamlit-component-lib'
  import { useStreamlit } from '../streamlit'

  // Automatically extract props as variables
  const props = defineProps(['args'])

  let myLayout = null
  let log_debug_info = false

  const graph = new Graph({ multi: true })

  const state = reactive({
    hoveredNode: "",
    hoveredNodeLabel: "",
    hoveredEdge: "",
    hoveredEdgeLabel: "",
    searchQuery: "",
    selectedNode: "",
    selectedEdge: "",
    lastselectedNode: "",
    lastselectedEdge: "",
    lastselectedNodeData: "",
    lastselectedEdgeData: "",
    suggestions: [],
    hoveredNeighbors: [],
    nnodes: 0,
    nedges: 0,
    positions: {},
  })

  let feature_flag_keep_hover_hightlighted = ref(true)

  //
  // Drag'n'drop feature
  // ~~~~~~~~~~~~~~~~~~~
  //

  // State for drag'n'drop
  let draggedNode = null;
  let isDragging = false;

  // detect changes in selected nodes or edges
  const change = computed(() => state?.lastselectedNode + state?.lastselectedEdge)
  watch(change, async () => {
    if(log_debug_info) { 
      console.log('updated state:', change.value)
    }

    syncStreamlit();

  })

  function syncStreamlit() { 
    if(log_debug_info) { console.log('syncStreamlit') }
    ////update state positions
    // state.positions = collectLayout(graph); // ??? DOES NOT WORK HERE
    if(log_debug_info) { console.log("syncStreamlit, positions:", state.positions) }
    // send data from component to Streamlit
    if(log_debug_info) { console.log('syncStreamlit, state:', state) }
    const stateJSON = JSON.parse(JSON.stringify(state)) // removes methods (non-clonable)

    Streamlit.setComponentValue(
      {
        graph: graph,
        state: stateJSON,
      }
    )
  }

  useStreamlit()

  onMounted(() => {
    const container = document.getElementById("sigma-container")
    const searchInput = document.getElementById("search-input")
    const searchSuggestions = document.getElementById("suggestions")

    // Initialize the graph with nodes and edges
    let graph = new Graph({ multi: true })
    graph.import({'nodes': props.args.nodes, 'edges': props.args.edges}) // dataJson.data)

    graph.nodes().forEach((node, i) => {
      // set default values for node attributes
      graph.setNodeAttribute(node, "id", node)
      graph.setNodeAttribute(node, "index", i)
      // graph.setNodeAttribute(node, "type", "square");
      graph.setNodeAttribute(node, "label", node.toString())
      graph.setNodeAttribute(node, "size", 10)
      // graph.setNodeAttribute(node, "color", "#000000")
    });

    graph.edges().forEach((edge, i) => {
      graph.setEdgeAttribute(edge, "index", i)
      graph.setEdgeAttribute(edge, "type", "arrow");
      // graph.setEdgeAttribute(edge, "label", edge.toString())
      // graph.setNodeAttribute(edge, "size", 5)
      // graph.setEdgeAttribute(edge, "color", "#000000");
    });

    if(log_debug_info) {
      console.log("props.args.positions (on mounted before assign): ", props.args.positions)
      console.log("state.positions (on mounted before assign): ", state.positions)
    }

    if ((props.args.positions) && (Object.keys(props.args.positions).length > 0)) {
      // If positions are provided, we assign them to the graph
      if(log_debug_info) {
        console.log("Positions provided, assigning them to the graph");
        console.log("    props.args.positions: ", props.args.positions)
      }
      assignLayout(graph, props.args.positions);

    } else {
      // If no positions are provided, we use circlepack layout
      if(log_debug_info) {
        console.log("No positions provided, using circlepack layout");
      }
      circlepack.assign(graph);
    }

    // // Force Atlas Layout
    // const settings = forceAtlas2.inferSettings(graph);
    // myLayout = new FA2Layout(graph, { settings });

    // Create the spring layout and start it
    myLayout = new ForceSupervisor(graph, { isNodeFixed: (_, attr) => attr.highlighted });
    myLayout.start();

    state.positions = collectLayout(graph);

    syncStreamlit();

    if(log_debug_info) {
      console.log("props.args.positions (on mounted after assign): ", props.args.positions)
      console.log("state.positions (on mounted after assign): ", state.positions)
    }
    let sigma_settings = {
      allowInvalidContainer: true,

      // Settings:
      // https://github.com/jacomyal/sigma.js/blob/13062dc5be4f876d7c188411b120bb5a3a0be6f4/packages/sigma/src/settings.ts

      renderLabels: true,
      enableEdgeEvents: true,
      renderEdgeLabels: true,

      defaultNodeType: 'pictogram',
      nodeProgramClasses: {
        pictogram: NodePictogramProgram,
      },

      ...props.args.settings

    }

    const render = new Sigma(graph, container, sigma_settings);

    // Action Buttons
    const startBtn = document.getElementById("start");
    const stopBtn = document.getElementById("stop");
    const resetBtn = document.getElementById("reset");
    const refreshBtn = document.getElementById("refresh");
    const syncBtn = document.getElementById("sync2st");
    startBtn.addEventListener("click", () => {
      myLayout.start();
    });
    stopBtn.addEventListener("click", () => {
      if (myLayout.isRunning) myLayout.stop();
    });
    resetBtn.addEventListener("click", () => {
      if (myLayout.isRunning) myLayout.stop();
      circlepack.assign(graph);
      render.refresh();
    });
    syncBtn.addEventListener("click", () => {
      state.positions = collectLayout(graph);
      if(log_debug_info) { console.log("sync button, positions:", state.positions) }
      syncStreamlit();
    });
    refreshBtn.addEventListener("click", () => {
      update_positions();
    });

    // Network dimensions
    state.nnodes = graph.nodes().length
    state.nedges = graph.edges().length

    // Feed the datalist autocomplete values:
    searchSuggestions.innerHTML = graph
      .nodes()
      .map((node) => `<option value="${graph.getNodeAttribute(node, "label")}"></option>`)
      .join("\n");

    // Actions:
    function setSearchQuery(query) {
      state.searchQuery = query;
      if (searchInput.value !== query) searchInput.value = query;
      if (query) {
        const lcQuery = query.toLowerCase();
        const suggestions = graph
          .nodes()
          .map((n) => ({ id: n, label: graph.getNodeAttribute(n, "label")}))
          .filter(({ label }) => label.toString().toLowerCase().includes(lcQuery));

        // If we have a single perfect match, them we remove the suggestions, and
        // we consider the user has selected a node through the datalist
        // autocomplete:
        if (suggestions.length === 1 && suggestions[0].label === query) {
          if(log_debug_info) { console.log("setSearchQuery, suggestions:", suggestions) }
          state.selectedNode = suggestions[0].id;
          state.lastselectedNode = suggestions[0].id;
          state.lastselectedNodeData = graph.getNodeAttributes(state.lastselectedNode);
          state.suggestions = undefined;
          setHoveredNode(state.selectedNode);

          // Move the camera to center it on the selected node:
          const nodePosition = render.getNodeDisplayData(state.selectedNode)
          render.getCamera().animate(nodePosition, {
            duration: 500,
          })
        }
        // Else, we display the suggestions list:
        else {
          state.selectedNode = null
          state.suggestions = new Set(suggestions.map(({ id }) => id))
        }
      }
      // If the query is empty, then we reset the selectedNode / suggestions state:
      else {
        state.selectedNode = undefined
        state.suggestions = undefined;
      }

      render.refresh({
        // We don't touch the graph data so we can skip its reindexation
        skipIndexation: true,
      });
    }

    function setHoveredNode(node) {
      if (node) {
        state.hoveredNode = node.node
        state.hoveredNodeLabel = graph.getNodeAttribute(node.node, 'label')
        // state.hoveredEdge = undefined
        // state.hoveredEdgeLabel = undefined
        state.hoveredNeighbors = graph.neighbors(node.node) // new Set(graph.neighbors(node))
      }

      if (!node) {
        state.hoveredNode = undefined
        state.hoveredNodeLabel = undefined
        // state.hoveredEdge = undefined
        // state.hoveredEdgeLabel = undefined
        state.hoveredNeighbors = undefined
      }

      render.refresh({
        // We don't touch the graph data so we can skip its reindexation
        skipIndexation: true,
      })

    }

    function resetHoveredNode() {
      state.hoveredNode = undefined
      state.hoveredNodeLabel = undefined
      state.hoveredEdge = undefined
      state.hoveredEdgeLabel = undefined
      state.hoveredNeighbors = undefined

      render.refresh({
        // We don't touch the graph data so we can skip its reindexation
        skipIndexation: true,
      })
    }

    function setHoveredEdge(edge) {
      if (edge) {
        // state.hoveredNode = undefined
        // state.hoveredNodeLabel = undefined
        state.hoveredEdge = edge.edge
        state.hoveredEdgeLabel = graph.getEdgeAttribute(edge.edge, 'label')
      }

      if (!edge) {
        // state.hoveredNode = undefined
        // state.hoveredNodeLabel = undefined
        state.hoveredEdge = undefined
        state.hoveredEdgeLabel = undefined
      }

      render.refresh({
        // We don't touch the graph data so we can skip its reindexation
        skipIndexation: true,
      })

    }

    function update_positions() {
      // if (myLayout.isRunning) myLayout.stop();
      assignLayout(graph, props.args.positions);
      state.positions = collectLayout(graph);
      syncStreamlit();
      render.refresh();
    }

    const handleMouseUp = () => {
      // On mouse up, we reset the dragging mode
      if (draggedNode) {
        graph.removeNodeAttribute(draggedNode, "highlighted");
      }
      isDragging = false;
      draggedNode = null;
    };

    // Bind search input interactions:
    searchInput.addEventListener("input", () => {
      setSearchQuery(searchInput.value || "")
    })
    searchInput.addEventListener("blur", () => {
      setSearchQuery("")
    })

    // Bind graph interactions

    // Nodes

    render.on("enterNode", (event) => {
      if(log_debug_info) { console.log("enterNode", event.node) }
      setHoveredNode(event)
    })
    render.on("leaveNode", (event) => {
      if(log_debug_info) { console.log("leaveNode") }
      if (!feature_flag_keep_hover_hightlighted) {
        setHoveredNode(undefined)
      }
    })
    render.on("upNode", handleMouseUp);

    render.on("downNode", (event) => {
      if(log_debug_info) { console.log("downNode", event.node) }
      // On mouse down on a node
      //  - we enable the drag mode
      //  - save in the dragged node in the state
      //  - highlight the node
      //  - disable the camera so its state is not updated
      // renderer.on("downNode", (e) => {
      isDragging = true;
      draggedNode = event.node;
      graph.setNodeAttribute(draggedNode, "highlighted", true);
      if (!render.getCustomBBox()) render.setCustomBBox(render.getBBox());
    })

    render.on("moveBody", (event) => {
      // if(log_debug_info) { console.log("moveBody", event) } // every mouse move
      // On mouse move, if the drag mode is enabled, we change the position of the draggedNode
      if (!isDragging || !draggedNode) return;
      // Get new position of node - NOK, not working
      const pos = render.viewportToGraph({ x: event.event.x, y: event.event.y });
      if(log_debug_info) { console.log("moveEvent", event) } // every mouse move
      if(log_debug_info) { console.log("movePos", pos) } // every mouse move
      graph.setNodeAttribute(draggedNode, "x", pos.x);
      graph.setNodeAttribute(draggedNode, "y", pos.y);  
      // Prevent sigma to move camera:
      event.preventSigmaDefault();
      // event.original.preventDefault();
      // event.original.stopPropagation();

      state.positions = collectLayout(graph);
      syncStreamlit()
      syncStreamlit()

    })

    render.on("clickNode", (event) => {
      if(log_debug_info) { console.log("clickNode", event.node) }
      state.lastselectedNode = event.node
      state.lastselectedNodeData = graph.getNodeAttributes(event.node)
      state.lastselectedEdge = null
      state.lastselectedEdgeData = null
      state.hoveredNeighbors = graph.neighbors(event.node) // new Set(graph.neighbors(node))
      if(log_debug_info) { console.log("Changed State:", state) }

      state.positions = collectLayout(graph);
      syncStreamlit()
      syncStreamlit()

    })

    // Edges

    render.on("enterEdge", (event) => {
      if(log_debug_info) { console.log("enterEdge", event.edge) }
      setHoveredEdge(event)
    })
    render.on("leaveEdge", () => {
      if(log_debug_info) { console.log("leaveEdge") }
      setHoveredEdge(undefined)
    })
    render.on("clickEdge", (event) => {
      if(log_debug_info) { console.log("clickEdge", event.edge) }
      state.lastselectedEdge = event.edge
      state.lastselectedEdgeData = graph.getEdgeAttributes(event.edge)
      state.lastselectedNode = null
      state.lastselectedNodeData = null
      state.hoveredNeighbors = null
      if(log_debug_info) { console.log("Changed State:", state) }

      state.positions = collectLayout(graph);
      if(log_debug_info) { console.log("sync click edge, positions:", state.positions) }
      syncStreamlit()
      syncStreamlit()
      if(log_debug_info) { console.log("Synced Streamlit after clickEdge") }

    })

    // Stage (is the overall container of the graph)

    render.on("downStage", (event) => {
      state.lastselectedEdge = null
      state.lastselectedEdgeData = null
      state.lastselectedNode = null
      state.lastselectedNodeData = null
      state.hoveredNeighbors = null
      if (feature_flag_keep_hover_hightlighted) {
        resetHoveredNode();
      }
      if(log_debug_info) { console.log("downStage", event.stage) }
    })
    render.on("upStage", handleMouseUp);

    render.on("clickStage", (event) => {
      if(log_debug_info) { console.log("clickStage", event.stage) }
      resetHoveredNode();
      state.lastselectedEdge = null
      state.lastselectedEdgeData = null
      state.lastselectedNode = null
      state.lastselectedNodeData = null
      state.hoveredNeighbors = null

      state.positions = collectLayout(graph);
      if(log_debug_info) { console.log("sync click stage, positions:", state.positions) }
      syncStreamlit()
      syncStreamlit()
    })

    // Reducers

    // Render nodes
    render.setSetting("nodeReducer", (node, data) => {
      const res = { ...data };

      if (node === state.hoveredNode) {
        res.size *= 1.5
      }

      if(state.hoveredNeighbors) {
        if (
          (Array.from(state.hoveredNeighbors).length>0) 
          && state.hoveredNode !== node) {
            if (!state.hoveredNeighbors.includes(node)) {
              res.label = ""
            } else {
              res.size *= 1.5
              res.forceLabel = true
            }
        }
      }

      if (state.hoveredEdge) {
        if (graph.extremities(state.hoveredEdge).includes(node)) {
          res.size *=1.5
          res.forceLabel = true
        } else {
          res.label = ""
        }
      }
      
      if (node === state.selectedNode) {
        res.highlighted = true;
      } else if (state.suggestions) {
        if (Array.from(state.suggestions.values()).length>0) {
          if (Array.from(state.suggestions.entries())[0][0]==node) {
            res.size *=1.5
            res.forceLabel = true;
          } else {
            res.label = ""
          }
        }
      }

      return res;
    });

    // Render edges
    render.setSetting("edgeReducer", (edge, data) => {
      const res = { ...data }

      res.size = 3

      if (edge === state.hoveredEdge) {
        res.color = "#aaaaff"
        res.size *= 2
        res.forceLabel = true
      }

      if (state.hoveredNode) {
        if (!graph.extremities(edge).every((n) => n === state.hoveredNode || graph.areNeighbors(n, state.hoveredNode))) {
          res.size = 1
        } else {
          res.color = "#aaaaff"
          res.size *= 1.5
          res.forceLabel = true
        }
      }
      if (state.suggestions) {
        if (
          (Array.from(state.suggestions.values()).length>0) &&
          (!Array.from(state.suggestions.values()).includes(graph.source(edge)) || !Array.from(state.suggestions.values()).includes(graph.target(edge)))
        ) {
          res.color = "#cccccc"
          res.label = ""
        }
      }

      return res;
    })
    
    syncStreamlit()

    render.refresh({
      // We don't touch the graph data so we can skip its reindexation
      skipIndexation: true,
    })

  })

  onUnmounted(() => {
    if (myLayout) {
      myLayout.kill()
      render.kill()
    }
  })

  defineExpose ({
      graph,
      state
  })

</script>
