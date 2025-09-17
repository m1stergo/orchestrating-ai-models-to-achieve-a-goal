<script setup lang="ts">
import { computed, ref } from 'vue'
import { useProductForm } from '@/composables/useProductForm'
import { useMutation, useQuery } from '@pinia/colada'
import { getSettings } from '../UserSettings/api'
import Button from 'primevue/button'
import ConfirmPopup from 'primevue/confirmpopup'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Stepper from 'primevue/stepper'
import StepItem from 'primevue/stepitem'
import Step from 'primevue/step'
import StepPanel from 'primevue/steppanel'
import Skeleton from 'primevue/skeleton'
import ProductContext from './ProductContext.vue'
import ProductDescription from './ProductDescription.vue'
import PromotionalAudio from './PromotionalAudio.vue'
import { useService } from '@/entities/services/useService'
import type { ExtractWebContentResponse } from './types'
import { extractWebContent } from './api'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

const props = defineProps<{ step?: number }>()

const form = useProductForm()

// get user settings
const { data: settings } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
  refetchOnWindowFocus: false,
})

const activeStep = ref(props.step || 1)

const toast = useToast()
const confirm = useConfirm();

const { mutateAsync: triggerExtractWebContent, isLoading: isLoadingExtractWebContent } = useMutation({
  mutation: extractWebContent,
  onSuccess: (response: ExtractWebContentResponse) => {
    form.setFieldValue('vendor_context', response.title)
    form.setFieldValue('vendor_url', response.url)
    form.setFieldValue('images', response.images)
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error extracting the content, please try again', life: 3000 })
  },
})

const describeImageService = useService('describe-image', {
    onSuccess: (response: any) => {
        form.setFieldValue('image_description', response.data)
    },
    onError: () => {
        toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error describing the image, please try again', life: 3000 })
    },
})

const generateDescriptionService = useService('generate-description', {
    onSuccess: (response: any) => {
        const parsed = parseJSON(response.data)
        form.setFieldValue('name', parsed.title)
        form.setFieldValue('description', parsed.description)
        form.setFieldValue('keywords', parsed.keywords)
        form.setFieldValue('category', parsed.category)
    },
    onError: () => {
        toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error generating the description, please try again', life: 3000 })
    },
})

const generateDescriptionLabel = computed(() => {
    if (form.values.description) {
        return 'Re-generate description'
    }  
    return 'Generate description'
})

const isLoadingProductDescription = computed(() => isLoadingExtractWebContent.value || describeImageService.isLoadingInference.value || generateDescriptionService.isLoadingInference.value)

function generateDescription() {
    if (form.values.selected_context_source === 'website' && form.values.vendor_url) {
        triggerExtractWebContent(form.values.vendor_url).then(() => {
            return describeImageService.run({
                image_url: form.values.images?.[0],
                model: settings.value?.describe_image_model,
                prompt: settings.value?.describe_image_prompt
            })
        }).then(() => {
            generateDescriptionService.run({
                text: form.values.image_description,
                model: settings.value?.generate_description_model,
                prompt: settings.value?.generate_description_prompt,
                categories: settings.value?.categories || []
            })
        })
    } else if (form.values.selected_context_source === 'image' && form.values.uploaded_image) {
        form.setFieldValue('images', [form.values.uploaded_image])
        describeImageService.run({
            image_url: form.values.uploaded_image,
            model: settings.value?.describe_image_model,
            prompt: settings.value?.describe_image_prompt
        }).then(() => {
            generateDescriptionService.run({
                text: form.values.image_description,
                model: settings.value?.generate_description_model,
                prompt: settings.value?.generate_description_prompt,
                categories: settings.value?.categories || []
            })
        })
    }
}

function handleGenerateDescription() {
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
                generateDescription()
                activeStep.value = 2
            },
            reject: () => {},
        })
    } else {
        generateDescription()
        activeStep.value = 2
    }
}

function parseJSON(text: string) {
    try {
        const parsed = JSON.parse(text)
        return {
            title: parsed.title || '',
            description: parsed.description || '',
            keywords: Array.isArray(parsed.keywords) ? parsed.keywords : [],
            category: parsed.category || ''
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error parsing the JSON, please try again', life: 3000 })
        return {
            title: '',
            description: '',
            keywords: [],
            category: ''
        }
    }
}
</script>

<template>
    <ConfirmPopup></ConfirmPopup>
    <div class="card">
        <Stepper v-model:value="activeStep">
            <StepItem :value="1">
                <Step>Select content source</Step>
                <StepPanel>
                    <ProductContext />
                        <Button 
                            class="w-full"
                            :severity="form.values.description ? 'primary' : 'help'" 
                            variant="outlined"
                            :disabled="!form.values.uploaded_image && !form.values.vendor_url" 
                            :loading="isLoadingExtractWebContent || describeImageService.isLoadingInference.value" 
                            :label="generateDescriptionLabel" 
                            @click="handleGenerateDescription" />
                </StepPanel>
            </StepItem>
            <StepItem :value="2">
                <Step :disabled="form.values.description === ''">Product description</Step>
                <StepPanel>
                    <div v-if="isLoadingProductDescription">
                        <div class="flex flex-col gap-2">
                            <Skeleton height="2rem"></Skeleton>
                            <Skeleton height="2rem"></Skeleton>
                            <Skeleton height="4rem"></Skeleton>
                        </div>
                    </div>
                    <ProductDescription v-else :categories="settings?.categories || []"/>
                </StepPanel>
            </StepItem>
            <StepItem :value="3">
                <Step :disabled="!form.values.description">Promotional audio</Step>
                <StepPanel>
                    <PromotionalAudio :prompt="settings?.generate_promotional_audio_script_prompt" :model="settings?.generate_description_model" />
                </StepPanel>
            </StepItem>
        </Stepper>
    </div>
</template>
