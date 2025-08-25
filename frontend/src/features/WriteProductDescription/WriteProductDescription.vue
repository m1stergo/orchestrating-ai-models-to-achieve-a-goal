<script setup lang="ts">
import { ref, computed, useTemplateRef } from 'vue'
import { Status } from './types'
import type { Product } from '@/entities/products'
import { useQuery } from '@pinia/colada'
import { getSettings } from '../UserSettings/api'
import Stepper from 'primevue/stepper'
import StepItem from 'primevue/stepitem'
import Step from 'primevue/step'
import StepPanel from 'primevue/steppanel'
import ExtractContent from './ExtractContent.vue'
import ProductDescription from './ProductDescription.vue'
import PromotionalAudio from './PromotionalAudio.vue'

const product = defineModel<Product>({required: true})

// get user settings
const { data: settings, isLoading: isLoadingSettings } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
  refetchOnWindowFocus: false,
})

const isEditMode = computed(() => !!product.value?.id)

const activeStep = ref(isEditMode.value ? 2 : 1)

// Extract content status
const extractContentStatus = ref<Status>(Status.PENDING)
const productDescriptionStatus = ref<Status>(Status.PENDING)
const promotionalAudioStatus = ref<Status>(Status.PENDING)


const isLoading = computed(() => {
    return isLoadingSettings.value || extractContentStatus.value === Status.PENDING || productDescriptionStatus.value === Status.PENDING || promotionalAudioStatus.value === Status.PENDING
})

const productDescription = useTemplateRef('productDescription')
const promotionalAudio = useTemplateRef('promotionalAudio')


function handleProductDescriptionStatusUpdate(status: Status) {
    productDescriptionStatus.value = status
}

function handleExtractContentStatusUpdate(status: Status) {
    extractContentStatus.value = status
    if (status === Status.SUCCESS) {
        activeStep.value = 2
        // productDescription.value?.generateDescription()
    }

}
</script>

<template>
    <div class="card">
        <Stepper v-model:value="activeStep">
            <StepItem :value="1">
                <Step>Select content source</Step>
                <StepPanel>
                    <ExtractContent 
                        ref="extractContent" 
                        v-model="product" 
                        :model="settings?.describe_image_model"
                        @update:status="handleExtractContentStatusUpdate"
                    />
                </StepPanel>
            </StepItem>
            <StepItem :value="2">
                <Step>Product description</Step>
                <StepPanel>
                    <ProductDescription 
                        ref="productDescription" 
                        v-model="product" 
                        :model="settings?.describe_image_model" 
                        @update:status="handleProductDescriptionStatusUpdate" 
                    />
                </StepPanel>
            </StepItem>
            <StepItem :value="3">
                <Step :disabled="!product.description">Promotional audio</Step>
                <StepPanel>
                    <PromotionalAudio 
                        v-model="product" 
                        :model="settings?.describe_image_model" 
                    />
                </StepPanel>
            </StepItem>
        </Stepper>
    </div>
</template>
