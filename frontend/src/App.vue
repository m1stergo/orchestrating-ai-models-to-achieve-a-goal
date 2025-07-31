<script setup lang="ts">
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
</script>

<template>
  <Toast position="top-center" />
  <RouterView />
</template>
<style>
html, body {
  background-color: var(--color-slate-100);
  height: 100%;
  overflow: hidden; 
}
</style>
