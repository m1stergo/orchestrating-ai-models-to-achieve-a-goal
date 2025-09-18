<script setup lang="ts">
import { ref, nextTick, provide, watch, computed } from 'vue'

import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
import Skeleton from 'primevue/skeleton'
import { WriteProductDescription } from '@/features/WriteProductDescription'
import { useMutation, useQueryCache, useQuery } from '@pinia/colada'
import { updateProduct, getProductById } from '@/entities/products/api'
import { useToast } from 'primevue/usetoast'
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import { UpdateProductSchema } from '@/entities/products';
import type { ProductFormData, UpdateProductFormData } from '@/entities/products'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import { useService } from '@/entities/services/useService'

const props = defineProps<{ id: number }>()
const queryCache = useQueryCache()
const toast = useToast()

const { data, refresh, isLoading } = useQuery({
  key: ['product', props.id],
  query: () => getProductById(props.id),
  enabled: false,
  refetchOnWindowFocus: false,
})

const {
  mutateAsync,
} = useMutation({
  mutation: updateProduct,
  onSettled: async () => {
    await queryCache.invalidateQueries({ key: ['products'], exact: true })
    nextTick(() => {
      toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Product updated successfully', life: 3000 });
    })
  },
  onError: () => {
    nextTick(() => {
      toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error updating the product, please try again', life: 3000 });
    })
  }
})

const visible = ref(false)

const validationSchema = toTypedSchema(UpdateProductSchema)

const form = useForm({
  validationSchema,
  initialValues: {
    name: '',
    sku: '',
    description: '',
    keywords: [],
    category: '',
    images: [],
    audio_description: null,
    audio: null,
    image_description: null,
    audio_config: null,
    additional_context: [],
    vendor_url: null,
    vendor_context: null,
    selected_context_source: null,
    uploaded_image: null
  },
})

provide('form', form)

const describeImageService = useService('describe-image')
const generateDescriptionService = useService('generate-description')

const isReady = computed(() => describeImageService.isReady.value && generateDescriptionService.isReady.value)
const error = computed(() => describeImageService.error.value || generateDescriptionService.error.value)


const onSubmit = form.handleSubmit(async (values) => {
  await mutateAsync(values as UpdateProductFormData)
  visible.value = false
})

watch(data, () => {
  form.setValues(data.value as ProductFormData)
})
</script>

<template>
  <Button :disabled="describeImageService.isLoadingSettings.value" icon="pi pi-pencil" rounded text size="small" @click="() => visible = true"/>
  <Drawer v-model:visible="visible" header="Edit Product" position="right" class="w-1/2" @show="refresh()">
    <Message v-if="error" severity="error" class="flex justify-center">
        <div class="flex items-center gap-2 justify-center text-center">
            An error occurred please try again later. {{ error }}
        </div>
    </Message>
    <Message v-else-if="!isReady" severity="warn" class="flex justify-center">
        <div class="flex items-center gap-2 justify-center text-center">
            <ProgressSpinner class="w-6 h-6" />
            Models are warming up, please wait a few seconds...
        </div>
    </Message> 
    <div v-else-if="isLoading" class="flex flex-col gap-4">
      <div class="flex flex-col gap-4">
        <Skeleton height="2rem" />
        <Skeleton height="2rem" />
      </div>
      <div class="flex flex-col">
        <Skeleton height="5rem" width="5rem" />
      </div>
      <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <Skeleton height="1.5rem" width="10rem" />
          <Skeleton height="2.5rem" />
        </div>
        <div class="flex flex-col gap-2">
          <Skeleton height="1.5rem" width="10rem" />
          <Skeleton height="2.5rem" />
        </div>
        <div class="flex flex-col gap-2">
          <Skeleton height="1.5rem" width="10rem" />
          <Skeleton height="6rem" />
        </div>
      </div>
    </div>
    <div v-else class="flex flex-col gap-4">
       <WriteProductDescription :step="2"/>
    </div>
    
    <template #footer v-if="true">
      <Button 
        :disabled="Object.keys(form.errors.value).length > 0" 
        type="submit" 
        label="Update Product" 
        class="w-full" 
        @click="onSubmit" 
      />
    </template>
  </Drawer>
</template>
