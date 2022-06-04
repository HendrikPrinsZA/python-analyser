<template>
  <div class="wrapper">
    <h1>WhatsApp Stats from {{ renderer }}</h1>

    Counter: {{ counter }} <button @click="exampleMethod">exampleMethod</button>
  </div>
</template>

<script>
export default {
  name: "WhatsApp",
  asyncData() {
    return {
      renderer: process.server ? "server" : "client",
      counter: 0
    }
  },

  mounted() {
    setInterval(() => {
      this.counter++
    }, 1000)
  },

  methods: {
    exampleMethod() {
      this.counter = this.counter + 100;
    }
  }
}
</script>

<style scoped>
.wrapper {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: red;

}
</style>
