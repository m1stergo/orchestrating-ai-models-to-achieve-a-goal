<script setup lang="ts">
import { watch } from 'vue'
import { useMutation } from '@pinia/colada'
import { generateDescription } from './api'
import type { Product } from '@/entities/products'
import { useToast } from 'primevue/usetoast'
import { Status } from './types'
import Skeleton from 'primevue/skeleton'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Chips from 'primevue/chips'

const emit = defineEmits(['update:status'])
    
const props = defineProps<{ model?: string }>()

const toast = useToast()

const product = defineModel<Product>({required: true})

const { mutateAsync: triggerGenerateDescription, isLoading, status: statusGenerateDescription } = useMutation({
  mutation: generateDescription,
  onSuccess: (data) => {
    product.value.description = data.description
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error generating the description, please try again', life: 3000 });
  },
})

watch(statusGenerateDescription, () => {
    if (statusGenerateDescription.value === Status.SUCCESS) {
        emit('update:status', Status.SUCCESS)
    }
    if (statusGenerateDescription.value === Status.ERROR) {
        emit('update:status', Status.ERROR)
    }
    if (statusGenerateDescription.value === Status.PENDING) {
        emit('update:status', Status.PENDING)
    } 
})

defineExpose({
    isLoading,
    generateDescription: () => {
        if (!product.value.description || !props.model) return
        triggerGenerateDescription({ text: product.value.description, model: props.model })
    }
})
</script>
<template>
    <!-- Show image after analysis, then description generation -->
    <div v-if="product?.images && product.images.length > 0" class="flex flex-col gap-2">
        <!-- Show the image -->
        <div class="flex gap-2">
            <div v-if="product?.images?.length > 0">
                <div v-for="image in product?.images" :key="image">
                    <img :src="image" alt="Image" class="w-24 rounded">
                </div>
            </div>
        </div>

        <!-- Show description generation skeleton or final description -->
        <div v-if="isLoading">
            <div class="flex flex-col gap-2">
                <Skeleton height="2rem"></Skeleton>
                <Skeleton height="4rem"></Skeleton>
            </div>
        </div>
        <div v-else class="flex flex-col gap-4">
            <!-- SKU -->
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">SKU</label>
                <InputText v-model="product.sku" placeholder="Enter product SKU" />
            </div>

            <!-- Product Name -->
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">Product Name</label>
                <InputText v-model="product.name" placeholder="Enter product name" />
            </div>

            <!-- Description -->
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">Description</label>
                <Textarea v-model="product.description" placeholder="Enter product description" class="border border-gray-300 rounded-md p-3 min-h-[100px] focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"/>
            </div>

            <!-- Keywords -->
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">Keywords</label>
                <Chips v-model="product.keywords" placeholder="Add keywords and press Enter" />
            </div>

            <!-- Category -->
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">Category</label>
                <InputText v-model="product.category" placeholder="Enter product category" />
            </div>
        </div>
    </div>
</template>