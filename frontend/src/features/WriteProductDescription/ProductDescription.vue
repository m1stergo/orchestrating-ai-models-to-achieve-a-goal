<script setup lang="ts">
import { useProductForm } from '@/composables/useProductForm'
import Skeleton from 'primevue/skeleton'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import AutoComplete from 'primevue/autocomplete'
import Select from 'primevue/select'
import Message from 'primevue/message'

defineProps<{ categories: string[] }>()
const form = useProductForm()
</script>
<template>
    <div class="flex flex-col gap-2">
        <!-- Show the image -->
        <div v-if="form?.values.images?.length ?? 0 > 0" class="flex gap-2 flex-wrap">
            <div v-for="image in form?.values.images" :key="image">
                <img :src="image" alt="Image" class="w-24 rounded">
            </div>
        </div>
        <div class="flex flex-col gap-4">
            <!-- SKU Field -->
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">SKU *</label>
                <InputText 
                    :modelValue="form.values.sku" 
                    @update:modelValue="form.setFieldValue('sku', $event)"
                    placeholder="Enter product SKU" 
                    :invalid="!!form.errors.value.sku"
                />
                <Message v-if="form.errors.value.sku" severity="error" :closable="false" size="small" variant="simple">
                    {{ form.errors.value.sku }}
                </Message>
            </div>

            <!-- Product Name Field -->
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">Product Name *</label>
                <InputText 
                    :modelValue="form?.values.name" 
                    @update:modelValue="form.setFieldValue('name', $event)"
                    placeholder="Enter product name" 
                    :invalid="!!form.errors.value.name"
                />
                <Message v-if="form.errors.value.name" severity="error" :closable="false" size="small" variant="simple">
                    {{ form.errors.value.name }}
                </Message>
            </div>

            <!-- Description Field -->
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">Description *</label>
                <Textarea 
                    :modelValue="form?.values.description" 
                    @update:modelValue="form.setFieldValue('description', $event)"
                    placeholder="Enter product description" 
                    class="border border-gray-300 rounded-md p-3 min-h-[100px] focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    :invalid="!!form.errors.value.description"
                    autoResize
                />
                <Message v-if="form.errors.value.description" severity="error" :closable="false" size="small" variant="simple">
                    {{ form.errors.value.description }}
                </Message>
            </div>

            <!-- Keywords Field -->
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">Keywords</label>
                <AutoComplete 
                    :modelValue="form?.values.keywords" 
                    @update:modelValue="form.setFieldValue('keywords', $event)"
                    placeholder="Add keywords and press Enter"
                    :multiple="true"
                    :typeahead="false"
                    :suggestions="[]"
                />
            </div>

            <!-- Category -->
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">Category</label>
                <Select 
                    :modelValue="form?.values.category" 
                    @update:modelValue="form.setFieldValue('category', $event)"
                    :options="categories"
                    placeholder="Select product category" 
                />
            </div>
        </div>
    </div>
</template>