<script setup lang="ts">
import { watch } from 'vue'
import { useMutation, useQuery } from '@pinia/colada'
import { generateDescription } from './api'
import { useProductForm } from '@/composables/useProductForm'
import { getSettings } from '@/features/UserSettings/api'
import { Status } from './types'
import Skeleton from 'primevue/skeleton'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import AutoComplete from 'primevue/autocomplete'
import Select from 'primevue/select'
import Message from 'primevue/message'

const emit = defineEmits(['update:status'])
    
const props = defineProps<{ model?: string }>()

const form = useProductForm()

const { data: userSettings } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
  refetchOnWindowFocus: false,
})

const { mutateAsync: triggerGenerateDescription, isLoading, status: statusGenerateDescription } = useMutation({
  mutation: generateDescription,
  onSuccess: ({ data }) => {
    debugger
    const parsedData = parseDescriptionResponse(data)
    form.setValues({
      name: parsedData.title || form?.values.name,
      description: parsedData.description,
      keywords: parsedData.keywords || form?.values.keywords,
      category: parsedData.category || form?.values.category,
    })
  },
})

function parseDescriptionResponse(description: string) {
  try {
    // Try to parse as JSON
    debugger
    const parsed = JSON.parse(description)
    
    // Validate that it has the expected structure
    if (typeof parsed === 'object' && parsed !== null) {
      return {
        title: parsed.title || '',
        description: parsed.description || description,
        keywords: Array.isArray(parsed.keywords) ? parsed.keywords : [],
        category: parsed.category || ''
      }
    }
  } catch (error) {
    console.warn('Failed to parse description as JSON:', error)
  }
  
  // Fallback: return original description with empty other fields
  return {
    title: '',
    description: description,
    keywords: [],
    category: ''
  }
}

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
        if (!form?.values.image_description || !props.model) return
        triggerGenerateDescription({ 
            text: form?.values.image_description, 
            model: props.model,
            prompt: userSettings.value?.generate_description_prompt || undefined,
            categories: userSettings.value?.categories || undefined
        })
    }
})
</script>
<template>
    <!-- Show image after analysis, then description generation -->
    <div v-if="form?.values.images && form.values.images.length > 0" class="flex flex-col gap-2">
        <!-- Show the image -->
        <div v-if="form?.values.images?.length > 0" class="flex gap-2 flex-wrap">
            <div v-for="image in form?.values.images" :key="image">
                <img :src="image" alt="Image" class="w-24 rounded">
            </div>
        </div>
        <!-- Show description generation skeleton or final description -->
        <div v-if="isLoading">
            <p class="text-sm">Generating product description...</p>
            <div class="flex flex-col gap-2">
                <Skeleton height="2rem"></Skeleton>
                <Skeleton height="4rem"></Skeleton>
            </div>
        </div>
        <div v-else class="flex flex-col gap-4">
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
                    :options="userSettings?.categories || []"
                    placeholder="Select product category" 
                />
            </div>
        </div>
    </div>
</template>