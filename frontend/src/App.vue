<script setup lang="ts">
import { watch } from 'vue'
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { useService } from '@/entities/services/useService'
import { onMounted } from 'vue'

const toast = useToast()

const describeImageService = useService('describe-image', {
  onError: () => {
    toast.add({
      severity: 'error',
      summary: 'Service Unavailable',
      detail: 'Unable to connect to image description service. Please refresh the page.',
    })
  }
})

const generateDescriptionService = useService('generate-description', {
  onError: () => {
    toast.add({
      severity: 'error',
      summary: 'Service Unavailable',
      detail: 'Unable to connect to generate description service. Please refresh the page.',
    })
  }
})

const { warmup: triggerWarmupGenerateAudio } = useService('text-to-speech', {
  onError: () => {
    toast.add({
      severity: 'error',
      summary: 'Service Unavailable',
      detail: 'Unable to connect to generate audio service. Please refresh the page.',
    })
  }
})

onMounted(() => {
  triggerWarmupGenerateAudio({ model: 'chatterbox' })
})

watch(describeImageService.settings, (newSettings, oldSettings) => {
  if (newSettings?.describe_image_model !== oldSettings?.describe_image_model && newSettings?.describe_image_model) {
    describeImageService.warmup({ model: newSettings.describe_image_model })
  }
})

watch(generateDescriptionService.settings, (newSettings, oldSettings) => {
  if (newSettings?.generate_description_model !== oldSettings?.generate_description_model && newSettings?.generate_description_model) {
    generateDescriptionService.warmup({ model: newSettings.generate_description_model })
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
