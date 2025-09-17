<script setup lang="ts">
import { ref, watch, computed, watchEffect } from 'vue'
import UploadImage from './UploadImage.vue'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { useProductForm } from '@/composables/useProductForm'
import type { ProductFormData } from '@/entities/products'

const form = useProductForm()

const contextSourceOptions = [
  { name: 'Image', value: 'image' },
  { name: 'Website URL', value: 'website' },
]
const selectedContextSource = ref<ProductFormData['selected_context_source']>(form.values.selected_context_source)

const selectedContextSourceComputed = computed({
    get: () => contextSourceOptions.find(option => option.value === selectedContextSource.value) || contextSourceOptions[0],
    set: (newValue) => {
        selectedContextSource.value = newValue.value
    }
})   

const vendorContext = ref<ProductFormData['vendor_context']>(form.values.vendor_context)
const vendorUrl = ref<ProductFormData['vendor_url']>(form.values.vendor_url)
const additionalContext = ref<Array<{key: string, value: string}>>(form.values.additional_context || [])
const uploadedImage = ref<ProductFormData['uploaded_image']>(form.values.uploaded_image)

function updateAditionalContext(index: number, field: 'key' | 'value', value: string) {
  
  const copy = [...additionalContext.value]
  copy[index][field] = value
  additionalContext.value = copy
  
  const lastIndex = additionalContext.value.length - 1
  if (index === lastIndex && additionalContext.value[lastIndex].key && additionalContext.value[lastIndex].value) {
    additionalContext.value.push({key: '', value: ''})
  }
} 

function removeAditionalContext(index: number) {
  if (additionalContext.value.length > 1) {
    additionalContext.value.splice(index, 1)
  }
}

watchEffect(() => {
  form.setFieldValue('selected_context_source', selectedContextSourceComputed.value.value)
})

watch(vendorContext, () => {
  form.setFieldValue('vendor_context', vendorContext.value)
})

watch(vendorUrl, () => {
  form.setFieldValue('vendor_url', vendorUrl.value)
})

watch(additionalContext, () => {
  form.setFieldValue('additional_context', additionalContext.value)
})

watch(uploadedImage, () => {
  form.setFieldValue('uploaded_image', uploadedImage.value)
})
</script>

<template>
  <div class="flex flex-col gap-4">
      <Select id="contextSource"
          v-model="selectedContextSourceComputed"
          :options="contextSourceOptions"
          optionLabel="name"
          placeholder="Select a content source"
          class="w-full" />
      <InputText v-if="selectedContextSourceComputed.value === 'website'" v-model="vendorUrl" placeholder="Enter a URL" />
      <UploadImage 
        v-if="selectedContextSourceComputed.value === 'image'" 
        v-model="uploadedImage" />
  </div>
  <div class="py-4">
    <p class="mb-2 text-sm font-medium">Additional context (key-value pairs)</p>
    <p class="text-sm text-gray-600">Provide specific details that cannot be inferred from the image, such as brand name, material composition, or special features</p>
    <div class="space-y-2">
      <div v-for="(pair, index) in additionalContext" :key="index" class="flex items-center gap-2">
        <InputText  
          class="flex-1 p-inputtext-sm" 
          size="small"
          :value="pair.key" 
          @input="event => updateAditionalContext(index, 'key', (event.target as HTMLInputElement).value)" 
          placeholder="Material" />
        <InputText 
          class="flex-1 p-inputtext-sm" 
          size="small"
          :value="pair.value" 
          @input="event => updateAditionalContext(index, 'value', (event.target as HTMLInputElement).value)" 
          placeholder="Dull copper" />
        <Button 
          v-if="additionalContext.length > 1" 
          icon="pi pi-times" 
          severity="danger" 
          text 
          rounded 
          @click="removeAditionalContext(index)" />
      </div>
    </div>
  </div>
</template>