<script setup lang="ts">
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { useDescribeImageService } from '@/entities/services/useDescribeImageService'

const toast = useToast()

useDescribeImageService({
  onError: () => {
    toast.add({
      severity: 'error',
      summary: 'Service Unavailable',
      detail: 'Unable to connect to image description service. Please refresh the page.',
    })
  }
})
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
