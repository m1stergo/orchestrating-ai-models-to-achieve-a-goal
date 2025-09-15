<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import UploadImage from './UploadImage.vue'
import type { ExtractWebContentResponse } from './types'
import { useMutation, useQuery } from '@pinia/colada'
import { extractWebContent } from './api'
import { getSettings } from '@/features/UserSettings/api'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmPopup from 'primevue/confirmpopup'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { Status } from './types'
import { useProductForm } from '@/composables/useProductForm'
import { useService } from '@/entities/services/useService'

const props = defineProps<{ model?: string }>()

const emit = defineEmits(['update:status'])

const form = useProductForm()

const contextPairs = ref<Array<{key: string, value: string}>>([{key: '', value: ''}])

const additionalContextString = computed(() => {
  return contextPairs.value
    .filter(pair => pair.key.trim() !== '' && pair.value.trim() !== '')
    .map(pair => [pair.key.trim(), pair.value.trim()].join(': ')).join(', ')
})

function updateContextPair(index: number, field: 'key' | 'value', value: string) {
  contextPairs.value[index][field] = value
  
  const lastIndex = contextPairs.value.length - 1
  if (index === lastIndex && contextPairs.value[lastIndex].key && contextPairs.value[lastIndex].value) {
    contextPairs.value.push({key: '', value: ''})
  }
}

function removeContextPair(index: number) {
  if (contextPairs.value.length > 1) {
    contextPairs.value.splice(index, 1)
  }
}

const { data: userSettings } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
  refetchOnWindowFocus: false,
})

const website = ref<ExtractWebContentResponse>({
    title: '',
    description: '',
    images: [],
    url: '',
})

const contentSourceOptions = [
  { name: 'Image', value: 'image' },
  { name: 'Website URL', value: 'website' },
]
const selectedContentSource = ref(contentSourceOptions[0])

const toast = useToast()
const confirm = useConfirm();

const uploadedImage = ref('')

const latestDescribeImageResponse = ref('')
const latestWebsiteUrl = ref('')
const latestUploadedImageUrl = ref('')

const { data: extractWebContentData, mutateAsync: triggerExtractWebContent, isLoading: isLoadingExtractWebContent } = useMutation({
  mutation: extractWebContent,
  onSuccess: (response: ExtractWebContentResponse) => {
    website.value = response
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error extracting the content, please try again', life: 3000 })
    emit('update:status', Status.FAILED)
  },
})

const describeImageService = useService('describe-image', {
  onSuccess: (response: any) => {
    latestDescribeImageResponse.value = response.data
    generateDescription()
  },
  onError: () => {
    emit('update:status', Status.FAILED)
  }
})

const buttonLabel = computed(() => {
  if (isLoadingExtractWebContent.value || describeImageService.isLoadingInference.value) {
    return 'Extracting content...'
  }
  return 'Extract content'
})

async function extractContent() {
    // Check if content already exists and ask for confirmation
    if (form.values.description) {
        confirm.require({
            message: 'This will overwrite the existing product description. Are you sure you want to continue?',
            header: 'Confirm Regeneration',
            icon: 'pi pi-exclamation-triangle',
            rejectProps: {
                label: 'Cancel',
                severity: 'secondary',
                outlined: true
            },
            acceptProps: {
                label: 'Continue',
                severity: 'danger'
            },
            accept: () => {
                performExtraction()
            },
            reject: () => {},
        })
    } else {
        performExtraction()
    }
}

async function performExtraction() {
    if (selectedContentSource.value.value === 'website') {
        if (!website.value.url || latestWebsiteUrl.value === website.value.url) return
        await triggerExtractWebContent(website.value.url)
        latestWebsiteUrl.value = website.value.url
    }
    else if (uploadedImage.value && latestUploadedImageUrl.value !== uploadedImage.value) {
      await describeImageService.run({
        image_url: uploadedImage.value,
        model: props.model!,
        prompt: userSettings.value?.describe_image_prompt
      })
      latestUploadedImageUrl.value = uploadedImage.value
    } else {
      generateDescription()
    }
}

function generateDescription() {
  if (selectedContentSource.value.value === 'website') {
      form.setValues({
        image_description: `
        # Context: ${additionalContextString.value}
        # Brief: ${extractWebContentData.value?.title}
        # Image description: ${latestDescribeImageResponse.value}
        `,
        images: extractWebContentData.value?.images!,
      })
    } else {
      form.setValues({
        image_description: `
        # Context: ${additionalContextString.value}
        # Image description: ${latestDescribeImageResponse.value}
        `,
        images: [uploadedImage.value],
      })
    }
    emit('update:status', Status.COMPLETED)
}
</script>

<template>
  <div class="flex flex-col gap-4">
      <Select id="contentSource"
          v-model="selectedContentSource"
          :options="contentSourceOptions"
          optionLabel="name"
          placeholder="Select a content source"
          class="w-full" />
      <InputText v-if="selectedContentSource.value === 'website'" v-model="website.url" placeholder="Enter a URL" />
      <UploadImage 
        v-if="selectedContentSource.value === 'image'" 
        v-model="uploadedImage" />
  </div>
  <div class="py-4">
    <p class="mb-2 text-sm font-medium">Additional context (key-value pairs)</p>
    <p class="text-sm text-gray-600">Provide specific details that cannot be inferred from the image, such as brand name, material composition, or special features</p>
    <div class="space-y-2">
      <div v-for="(pair, index) in contextPairs" :key="index" class="flex items-center gap-2">
        <InputText 
          class="flex-1 p-inputtext-sm" 
          size="small"
          :value="pair.key" 
          @input="event => updateContextPair(index, 'key', (event.target as HTMLInputElement).value)" 
          placeholder="Material" />
        <InputText 
          class="flex-1 p-inputtext-sm" 
          size="small"
          :value="pair.value" 
          @input="event => updateContextPair(index, 'value', (event.target as HTMLInputElement).value)" 
          placeholder="Dull copper" />
        <Button 
          v-if="contextPairs.length > 1" 
          icon="pi pi-times" 
          severity="danger" 
          text 
          rounded 
          @click="removeContextPair(index)" />
      </div>
    </div>
  </div>
  <div class="py-6">
    <Button 
      class="w-full"
      :severity="form.values.description ? 'primary' : 'help'" 
      variant="outlined"
      :disabled="!uploadedImage && !website.url" 
      :loading="isLoadingExtractWebContent || describeImageService.isLoadingInference.value" 
      :label="buttonLabel" 
      @click="extractContent" />
    <ConfirmPopup></ConfirmPopup>
  </div>
</template>