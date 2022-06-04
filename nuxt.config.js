export default {
  server: {
    port: 3000 // default
  },
  
  ssr: true, // Server-side rendering (maybe needed?)

  // Global page headers
  // see https://go.nuxtjs.dev/config-head
  head: {
    title: 'python-analyser-nuxt',
    htmlAttrs: {
      lang: 'en',
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
      { name: 'format-detection', content: 'telephone=no' },
    ],
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }],
  },

  // Global CSS
  // see https://go.nuxtjs.dev/config-css
  css: [],

  // Plugins to run before rendering page
  // see https://go.nuxtjs.dev/config-plugins
  plugins: [],

  components: true,

  buildModules: [
    '@nuxtjs/tailwindcss',
  ],

  modules: [
    '@nuxtjs/axios',
  ],

  axios: {
    baseURL: '/',
  },

  build: {},
}
