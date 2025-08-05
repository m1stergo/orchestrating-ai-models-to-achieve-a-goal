<script setup lang="ts">
import { ref, reactive, computed, watch, useTemplateRef, watchEffect } from 'vue'
import ExtractContentFromWebsite from './ExtractContentFromWebsite.vue'
import UploadImage from './UploadImage.vue'
import type { ExtractWebContentResponse, UploadImageResponse } from './types'
import { useMutation, useQuery } from '@pinia/colada'
import { describeImage, generateDescription, extractWebContent } from './api'
import { useToast } from 'primevue/usetoast'
import { getSettings } from '../SetSettings/api'
import Stepper from 'primevue/stepper'
import StepItem from 'primevue/stepitem'
import Step from 'primevue/step'
import StepPanel from 'primevue/steppanel'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import ProgressSpinner from 'primevue/progressspinner'

// Content source selection
const contentSourceOptions = [
  { name: 'Extract from website', value: 'website' },
  { name: 'Upload image', value: 'image' }
]
const selectedContentSource = ref(contentSourceOptions[0])

const toast = useToast()

const source = reactive<ExtractWebContentResponse>({
    title: '',
    description: '',
    images: [],
    url: '',
})

// Obtener las configuraciones del usuario
const { data: settings } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
})

const uploadedImage = ref('')

const status = ref({
    isLoadingExtractWebContent: true,
    isLoadingDescribeImage: true,
    isLoadingGenerateDescription: true,
})
  
const { data: extractWebContentData, mutateAsync: triggerExtractWebContent } = useMutation({
  mutation: extractWebContent,
  onSuccess: (data) => {
    status.value.isLoadingExtractWebContent = false
    source.images = data.images
    source.url = data.url
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error extracting the content, please try again', life: 3000 })
  },
})

const { data: imageDescriptionData, mutateAsync: triggerDescribeImage } = useMutation({
  mutation: describeImage,
  onSuccess: () => {
    status.value.isLoadingDescribeImage = false
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error describing the image, please try again', life: 3000 });
  },
})

const { mutateAsync: triggerGenerateDescription } = useMutation({
  mutation: generateDescription,
  onSuccess: (data) => {
    status.value.isLoadingGenerateDescription = false
    source.description = data.text
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error generating the description, please try again', life: 3000 });
  },
})

const beginProcessEnabled = computed(() => {
  if (selectedContentSource.value.value === 'website') {
    return source.url !== ''
  }
  if (selectedContentSource.value.value === 'image') {
    return uploadedImage.value !== ''
  }
  return false
})

const activeStep = ref(1)
const generateDescriptionEnabled = ref(false)


async function beginProcess() {
    status.value.isLoadingExtractWebContent = true
    status.value.isLoadingDescribeImage = true
    status.value.isLoadingGenerateDescription = true
    generateDescriptionEnabled.value = true
    activeStep.value = 2
    source.title = ''
    source.description = ''

    if (selectedContentSource.value.value === 'website') {
        if (!source.url) return
        await triggerExtractWebContent(source.url)
    }

    if (!source.images.length) return
    await triggerDescribeImage({
        image_url: source.images[0],
        model: settings.value?.describe_image_model || ''
    })

    if (!imageDescriptionData.value?.description) return
    await triggerGenerateDescription({
        text: extractWebContentData.value?.title + ' ' + imageDescriptionData.value?.description,
        model: settings.value?.generate_description_model || ''
    })
}

watch(uploadedImage, () => {
    if (uploadedImage.value) {
        source.images = [uploadedImage.value]
    }
})
</script>

<template>
    <div class="card">
        <Stepper v-model:value="activeStep">
            <StepItem :value="1">
                <Step>Select content source</Step>
                <StepPanel>
                    <div class="flex flex-col gap-2">
                        <Dropdown id="contentSource"
                            v-model="selectedContentSource"
                            :options="contentSourceOptions"
                            optionLabel="name"
                            placeholder="Select a content source"
                            class="w-full" />
                        <InputText v-if="selectedContentSource.value === 'website'" v-model="source.url" placeholder="Enter a URL" />
                        <UploadImage v-if="selectedContentSource.value === 'image'" v-model="uploadedImage" />
                    </div>
                    <div class="py-6">
                        <Button :disabled="!beginProcessEnabled" label="Generate description" @click="beginProcess" />
                    </div>
                </StepPanel>
            </StepItem>
            <StepItem :value="2">
                <Step :disabled="!generateDescriptionEnabled">Product description</Step>
                <StepPanel>
                    <div v-if="selectedContentSource.value === 'website'" class="flex items-center gap-2">
                        <ProgressSpinner v-if="status.isLoadingExtractWebContent" strokeWidth="4" style="width: 25px; height: 25px" />
                        <i v-else class="pi pi-check" />
                        <p class="text-sm w-full">Extracting content...</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <ProgressSpinner v-if="status.isLoadingDescribeImage" strokeWidth="4" style="width: 25px; height: 25px" />
                        <i v-else class="pi pi-check" />
                        <p class="text-sm w-full">Analyzing image...</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <ProgressSpinner v-if="status.isLoadingGenerateDescription" strokeWidth="4" style="width: 25px; height: 25px" />
                        <i v-else class="pi pi-check" />
                        <p class="text-sm w-full">Generating product description...</p>
                    </div>
                    <div v-if="status.isLoadingGenerateDescription">
                        <div class="flex flex-col gap-2">
                            <div class="flex gap-2">
                                <Skeleton size="5rem" v-for="i in 3" :key="i"></Skeleton>
                            </div>
                            <Skeleton height="2rem"></Skeleton>
                            <Skeleton height="4rem"></Skeleton>
                        </div>
                    </div>
                    <div v-else class="flex flex-col gap-2">
                        <div class="flex gap-2">
                            <div v-if="source.images.length > 0">
                                <div v-for="image in source.images" :key="image">
                                    <img :src="image" alt="Image" class="w-24 rounded">
                                </div>
                            </div>
                            <div v-else>
                                <img :src="mainImage" alt="Main Image" class="w-24 rounded">
                            </div>
                        </div>
                        <div v-html="source.description" contenteditable="true" />
                    </div>
                </StepPanel>
            </StepItem>
        </Stepper>
    </div>
</template>
