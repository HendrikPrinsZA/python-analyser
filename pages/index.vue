<template>
  <div>
    <NavTop/>
    
    Welcome, rendered from {{ renderer }}
  </div>
</template>

<script>
import NavTop from '~/components/NavTop.vue';
export default {
  name: "Home",
  asyncData() {
    return {
      renderer: process.server ? "server" : "client"
    };
  },
  components: { NavTop }
}
</script>
