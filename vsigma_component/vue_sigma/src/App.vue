<template>
  <div id="app">
    <WithStreamlitConnection v-slot="{ args }">
      <VSigma :args="args" />
    </WithStreamlitConnection>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue"
import VSigma from "./components/VSigma.vue"

// "withStreamlitConnection" is a scoped slot. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection.

import WithStreamlitConnection from "./streamlit/WithStreamlitConnection.vue"

export default defineComponent({
  name: "App",
  components: {
    VSigma,
    WithStreamlitConnection,
  },
})
</script>

<style>
body {
  margin: 0px;
}
#app {
  color: var(--text-color);
  font-family: var(--font);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
