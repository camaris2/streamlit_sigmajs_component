<template>
  <div class="graph">
    <div class="feedback">{{ state.nnodes }} Nodes - {{ state.nedges }} Edges</div>
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
    <div class="feedback">
      <button v-if="log_debug_info" @click="toggleDisplay('info01')">i</button>
      <div v-if="log_debug_info" class="debuginfo" id="info01">
        <div>Selected Node: {{ state.lastselectedNode }} : {{ state.lastselectedNodeData }}</div>
        <div>Selected Edge: {{ state.lastselectedEdge }} : {{ state.lastselectedEdgeData }}</div>
        <hr/>
        <div>State : {{ state }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { NodePictogramProgram } from "@sigma/node-image";
  // import getNodePictogramProgram from "sigma/rendering/webgl/programs/node.image";
  import Graph from "graphology";
  import { circlepack } from "graphology-layout";
  import FA2Layout from "graphology-layout-forceatlas2/worker";
  import forceAtlas2 from "graphology-layout-forceatlas2";
  import Sigma from "sigma";
  import { onMounted, onUnmounted, reactive, ref, watch, computed } from "vue";
  import { Streamlit } from 'streamlit-component-lib'
  import { useStreamlit } from '../streamlit'

  // Automatically extract props as variables
  const props = defineProps(['args'])

  let fa2Layout = null
  let log_debug_info = true

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
  })

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
    if(log_debug_info) { console.log('updated state:', change.value) }
    syncSreamlit()
  })

  function syncSreamlit() { 
    // send data from component to Streamlit
    if(log_debug_info) { console.log('state:', state) }
    const stateJSON = JSON.parse(JSON.stringify(state)) // removes methods (non-clonable)
    Streamlit.setComponentValue(
      {
        graph: graph,
        state: stateJSON,
      }
    )
  }

  function toggleDisplay(id){
    // var el = event.target
    var el = document.getElementById(id)
    if (el.style.visibility == "hidden") {
      el.style.visibility = "visible"
    } else {
      el.style.visibility = "hidden"
    }
  }

  useStreamlit()

  onMounted(() => {
    const container = document.getElementById("sigma-container")
    const searchInput = document.getElementById("search-input")
    const searchSuggestions = document.getElementById("suggestions")

    graph.import({'nodes': props.args.nodes, 'edges': props.args.edges}) // dataJson.data)

    graph.nodes().forEach((node, i) => {
      graph.setNodeAttribute(node, "index", i)
      // graph.setEdgeAttribute(node, "type", "square");
      // graph.setNodeAttribute(node, "label", node.toString())
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

    circlepack.assign(graph);
    const settings = forceAtlas2.inferSettings(graph);
    fa2Layout = new FA2Layout(graph, { settings });

    let sigma_settings = {
      allowInvalidContainer: true,
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
    startBtn.addEventListener("click", () => {
      fa2Layout.start();
    });
    stopBtn.addEventListener("click", () => {
      if (fa2Layout.isRunning) fa2Layout.stop();
    });
    resetBtn.addEventListener("click", () => {
      if (fa2Layout.isRunning) fa2Layout.stop();
      circlepack.assign(graph);
      render.refresh();
    });

    // Network dimensions
    state.nnodes = graph.nodes().length
    state.nedges = graph.edges().length
    if(log_debug_info) { console.log('nodes:', state.nnodes, 'edges:', state.nedges) }

    // Feed the datalist autocomplete values:
    searchSuggestions.innerHTML = graph
      .nodes()
      .map((node) => `<option value="${graph.getNodeAttribute(node, "label")}"></option>`)
      .join("\n");
    console.log(graph)
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
          // console.log(suggestions[0]);
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
      setHoveredNode(undefined)
    })
    const handleUp = () => {
      // On mouse up, we reset the dragging mode
      if (draggedNode) {
        graph.removeNodeAttribute(draggedNode, "highlighted");
      }
      isDragging = false;
      draggedNode = null;
    };
    render.on("upNode", handleUp);
    render.on("upStage", handleUp);

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
      event.original.preventDefault();
      event.original.stopPropagation();
    })
    render.on("clickNode", (event) => {
      if(log_debug_info) { console.log("clickNode", event.node) }
      state.lastselectedNode = event.node
      state.lastselectedNodeData = graph.getNodeAttributes(event.node)
      state.lastselectedEdge = null
      state.lastselectedEdgeData = null
      state.hoveredNeighbors = graph.neighbors(event.node) // new Set(graph.neighbors(node))
      if(log_debug_info) { console.log("Changed State:", state) }
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
    })

    // Stage (is the overall container of the graph)
    render.on("downStage", (event) => {
      state.lastselectedEdge = null
      state.lastselectedEdgeData = null
      state.lastselectedNode = null
      state.lastselectedNodeData = null
      state.hoveredNeighbors = null
      if(log_debug_info) { console.log("downStage", event.stage) }
    })

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
  })

  onUnmounted(() => {
    if (fa2Layout) {
      fa2Layout.kill()
      render.kill()
    }
  })

  defineExpose ({
      graph,
      state
  })

</script>

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
.feedback {
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
  height: 400px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
}
button + button {
  margin-left: 10px;
}
</style>
