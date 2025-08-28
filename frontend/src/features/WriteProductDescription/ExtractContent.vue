<script setup lang="ts">
import { ref, watch } from 'vue'
import UploadImage from './UploadImage.vue'
import type { ExtractWebContentResponse } from './types'
import { useMutation, useQuery } from '@pinia/colada'
import { describeImage, extractWebContent } from './api'
import { getSettings } from '@/features/UserSettings/api'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmPopup from 'primevue/confirmpopup'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'
import Message from 'primevue/message'
import { Status } from './types'
import { useProductForm } from '@/composables/useProductForm'

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

const { mutateAsync: triggerDescribeImage, isLoading: isLoadingDescribeImage, status: statusDescribeImage } = useMutation({
  mutation: describeImage,
  onSuccess: (data) => {
    if (selectedContentSource.value.value === 'website') {
      form.setValues({
        image_description: 'Listing description: ' + extractWebContentData.value?.title + ' ' + 'Image description: ' +  data.description!,
        images: extractWebContentData.value?.images!,
      })
    } else {
      form.setValues({
        image_description: data.description!,
        images: [uploadedImage.value],
      })
    }
  },
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
        await triggerDescribeImage({
            image_url: extractWebContentData.value?.images[0]!,
            model: props.model,
            prompt: userSettings.value?.describe_image_prompt
        })
    } else if (uploadedImage.value) {
        await triggerDescribeImage({
            image_url: uploadedImage.value,
            model: props.model,
            prompt: userSettings.value?.describe_image_prompt
        })
    }
}

watch(statusDescribeImage, () => {
    if (statusDescribeImage.value === Status.SUCCESS) {
        console.log('Extract content success')
        emit('update:status', Status.SUCCESS)
    }
    if (statusDescribeImage.value === Status.ERROR) {
        emit('update:status', Status.ERROR)
    }
    if (statusDescribeImage.value === Status.PENDING) {
        emit('update:status', Status.PENDING)
    }
})
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
      :loading="isLoadingExtractWebContent || isLoadingDescribeImage" 
      :label="(isLoadingExtractWebContent || isLoadingDescribeImage) ? 'Extracting content...' : 'Extract content'" 
      @click="extractContent" />
    <ConfirmPopup></ConfirmPopup>
  </div>
  <Message  v-if="model === 'qwen' && isAutoRetrying && !isLoadingDescribeImage" severity="warn" class="flex justify-center">
    <div class="flex items-center gap-2 justify-center text-center">
      <ProgressSpinner class="w-6 h-6" />
      Qwen model is warming up, please wait a few seconds...
    </div>
  </Message>
</template>