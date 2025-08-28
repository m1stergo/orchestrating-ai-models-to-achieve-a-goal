<script setup lang="ts">
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
import { useService } from '@/entities/services/useService'
import { useQuery } from '@pinia/colada'
import { getSettings } from '@/features/UserSettings/api'
import { watch } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const { data: settings } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
  refetchOnWindowFocus: false,
})
const { model: describeImageModel, error: describeImageError } = useService('describeImage')
const { model: generateDescriptionModel, error: generateDescriptionError } = useService('generateDescription')

watch(settings, () => {
    describeImageModel.value = settings.value?.describe_image_model || ''
    generateDescriptionModel.value = settings.value?.generate_description_model || ''
})

watch(describeImageError, () => {
    if (describeImageError.value) {
        toast.add({
            severity: 'error',
            summary: 'Service Unavailable',
            detail: 'Unable to connect to image description service. Please refresh the page.',
        })
    }
})
watch(generateDescriptionError, () => {
    if (generateDescriptionError.value) {
        toast.add({
            severity: 'error',
            summary: 'Service Unavailable',
            detail: 'Unable to connect to product description service. Please refresh the page.',
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
