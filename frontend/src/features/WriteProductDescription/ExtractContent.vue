<script setup lang="ts">
import { ref } from 'vue'
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
import { useDescribeImageService } from '@/entities/services/useDescribeImageService'

const props = defineProps<{ model?: string }>()

const emit = defineEmits(['update:status'])

const form = useProductForm()

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

const { data: extractWebContentData, mutateAsync: triggerExtractWebContent, isLoading: isLoadingExtractWebContent } = useMutation({
  mutation: extractWebContent,
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error extracting the content, please try again', life: 3000 })
    emit('update:status', Status.ERROR)
  },
})

const { describeImage, isLoading } = useDescribeImageService({
  onSuccess: (response: any) => {
    if (selectedContentSource.value.value === 'website') {
      form.setValues({
        image_description: 'Listing description: ' + extractWebContentData.value?.title + ' ' + 'Image description: ' +  response.data!,
        images: extractWebContentData.value?.images!,
      })
    } else {
      form.setValues({
        image_description: response.data!,
        images: [uploadedImage.value],
      })
    }
    emit('update:status', Status.SUCCESS)
  },
  onError: () => {
    emit('update:status', Status.ERROR)
  }
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
        if (!website.value.url) return
        await triggerExtractWebContent(website.value.url)
        describeImage({
            image_url: extractWebContentData.value?.images[0]!,
            model: props.model!,
            prompt: userSettings.value?.describe_image_prompt
        })
    } else if (uploadedImage.value) {
      describeImage({
          image_url: uploadedImage.value,
          model: props.model!,
          prompt: userSettings.value?.describe_image_prompt
      })
    }
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
      <UploadImage v-if="selectedContentSource.value === 'image'" v-model="uploadedImage" />
  </div>

  <div class="py-6">
    <Button 
      class="w-full"
      :severity="form.values.description ? 'primary' : 'help'" 
      variant="outlined"
      :disabled="!uploadedImage && !website.url" 
      :loading="isLoadingExtractWebContent || isLoading" 
      :label="(isLoadingExtractWebContent || isLoading) ? 'Extracting content...' : 'Extract content'" 
      @click="extractContent" />
    <ConfirmPopup></ConfirmPopup>
  </div>
</template>