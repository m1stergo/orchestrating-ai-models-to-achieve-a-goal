<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { Status } from './types'
import { useProductForm } from '@/composables/useProductForm'
import { useQuery } from '@pinia/colada'
import { getSettings } from '../UserSettings/api'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Stepper from 'primevue/stepper'
import StepItem from 'primevue/stepitem'
import Step from 'primevue/step'
import StepPanel from 'primevue/steppanel'
import ExtractContent from './ExtractContent.vue'
import ProductDescription from './ProductDescription.vue'
import PromotionalAudio from './PromotionalAudio.vue'
import { useService } from '@/entities/services/useService'

const props = defineProps<{ step?: number }>()

const form = useProductForm()

// get user settings
const { data: settings } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
  refetchOnWindowFocus: false,
})

const activeStep = ref(props.step || 1)

// Extract content status
const extractContentStatus = ref<Status>(Status.PENDING)
const productDescriptionStatus = ref<Status>(Status.PENDING)

const { 
    isWarmingUp: isWarmingUpDescribeImageService, 
    error: errorDescribeImageService, 
} = useService('describe-image')

const productDescription = useTemplateRef('productDescription')


function handleProductDescriptionStatusUpdate(status: Status) {
    productDescriptionStatus.value = status
}

function handleExtractContentStatusUpdate(status: Status) {
    extractContentStatus.value = status
    if (status === Status.SUCCESS) {
        activeStep.value = 2
        productDescription.value?.generateDescription()
    }
}
</script>

<template>
    <Message v-if="isWarmingUpDescribeImageService" severity="warn" class="flex justify-center">
        <div class="flex items-center gap-2 justify-center text-center">
            <ProgressSpinner class="w-6 h-6" />
            Models are warming up, please wait a few seconds...
        </div>
    </Message> 
    <Message v-else-if="errorDescribeImageService" severity="error" class="flex justify-center">
        <div class="flex items-center gap-2 justify-center text-center">
            An error occurred please try again later.
        </div>
    </Message>
    <div v-else class="card">
        <Stepper v-model:value="activeStep">
            <StepItem :value="1">
                <Step>Select content source</Step>
                <StepPanel>
                    <ExtractContent 
                        ref="extractContent" 
                        :model="settings?.describe_image_model"
                        @update:status="handleExtractContentStatusUpdate"
                    />
                </StepPanel>
            </StepItem>
            <StepItem :value="2">
                <Step :disabled="extractContentStatus !== Status.SUCCESS && form.values.description === ''">Product description</Step>
                <StepPanel>
                    <ProductDescription 
                        ref="productDescription" 
                        :model="settings?.generate_description_model" 
                        @update:status="handleProductDescriptionStatusUpdate" 
                    />
                </StepPanel>
            </StepItem>
            <StepItem :value="3">
                <Step :disabled="!form.values.description">Promotional audio</Step>
                <StepPanel>
                    <PromotionalAudio 
                        :model="settings?.generate_description_model" 
                    />
                </StepPanel>
            </StepItem>
        </Stepper>
    </div>
</template>
