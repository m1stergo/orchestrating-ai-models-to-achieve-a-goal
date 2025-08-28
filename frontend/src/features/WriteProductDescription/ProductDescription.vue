<script setup lang="ts">
import { watch, ref } from 'vue'
import { useMutation, useQuery } from '@pinia/colada'
import { generateDescription, warmupMistralModel } from './api'
import { useProductForm } from '@/composables/useProductForm'
import { getSettings } from '@/features/UserSettings/api'
import { useToast } from 'primevue/usetoast'
import { Status } from './types'
import Skeleton from 'primevue/skeleton'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import AutoComplete from 'primevue/autocomplete'
import Select from 'primevue/select'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'


const emit = defineEmits(['update:status'])
    
const props = defineProps<{ model?: string }>()

const toast = useToast()

const form = useProductForm()

// Auto-retry state for Mistral
const retryAttempts = ref(0)
const maxRetryAttempts = 3
const isAutoRetrying = ref(false)
const hasExecutedWarmup = ref(false)

const { data: userSettings } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
  refetchOnWindowFocus: false,
})

const { mutateAsync: triggerGenerateDescription, isLoading, status: statusGenerateDescription, error: errorGenerateDescription } = useMutation({
  mutation: generateDescription,
  onSuccess: (data) => {
    // Reset retry state on success
    retryAttempts.value = 0
    isAutoRetrying.value = false
    
    const parsedData = parseDescriptionResponse(data.text)
    form.setValues({
      name: parsedData.title || form?.values.name,
      description: parsedData.description,
      keywords: parsedData.keywords || form?.values.keywords,
      category: parsedData.category || form?.values.category,
    })
  },
})

const { mutateAsync: triggerWarmupMistral } = useMutation({
  mutation: warmupMistralModel,
  onSuccess: () => {
    hasExecutedWarmup.value = true
  },
  onError: (error) => {
    toast.add({ 
      severity: 'error', 
      summary: 'Warmup Error', 
      detail: error.message, 
      life: 3000 
    })
  },
})

function parseDescriptionResponse(description: string) {
  try {
    // Try to parse as JSON
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

// Function to perform retry with recursive logic
async function performRetryWithWarmup() {
  if (retryAttempts.value >= maxRetryAttempts) {
    isAutoRetrying.value = false
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error generating the description, please try again', life: 3000 });
    emit('update:status', Status.ERROR)
    return
  }

  // Execute warmup if not done yet
  if (!hasExecutedWarmup.value) {
    await triggerWarmupMistral()
  }
  
  // Wait 20 seconds before retrying
  setTimeout(async () => {
    try {
      await triggerGenerateDescription({ 
        text: form?.values.image_description!, 
        model: props.model!,
        prompt: userSettings.value?.generate_description_prompt || undefined,
        categories: userSettings.value?.categories || undefined
      })
    } catch (retryError) {
      // Recursively retry if still within attempts
      retryAttempts.value++
      await performRetryWithWarmup()
    }
  }, 20000) // 20 seconds
}

// Watch for errors in generate description to handle auto-retry for Mistral
watch(errorGenerateDescription, async (error) => {
  if (!error || isAutoRetrying.value) return
  if (props.model === 'mistral' && retryAttempts.value < maxRetryAttempts) {
    isAutoRetrying.value = true
    retryAttempts.value++
    await performRetryWithWarmup()
  }
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
        <Message v-if="model === 'mistral' && isAutoRetrying && !isLoading" severity="warn" class="flex justify-center">
            <div class="flex items-center gap-2 justify-center text-center">
                <ProgressSpinner class="w-6 h-6" />
                Mistral model is warming up, please wait a few seconds...
            </div>
        </Message>  
        <!-- Show description generation skeleton or final description -->
        <div v-else-if="isLoading">
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