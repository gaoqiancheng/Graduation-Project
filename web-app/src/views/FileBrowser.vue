<!-- views/NewPage.vue -->
<template>
  <BackgroundLayout>

  </BackgroundLayout>
  </template>
  
  <script>
  import BackgroundLayout from '@/components/BackgroundLayout.vue'
  export default {
    name: 'FileBrowser',
    components :{
      BackgroundLayout
    },
  }
  </script>
  
  <style scoped>
  .simple-page {
    padding: 20px;
    color: white;
    background: #0a0a1a;
    min-height: 100vh;
  }
  </style>