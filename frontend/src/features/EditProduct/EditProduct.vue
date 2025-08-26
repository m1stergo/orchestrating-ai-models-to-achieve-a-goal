<script setup lang="ts">
import { ref, nextTick, provide, watch } from 'vue'

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

const props = defineProps<{ id: number }>()
const queryCache = useQueryCache()
const toast = useToast()

const { data, isLoading, refresh } = useQuery({
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
  audio_description: '',
  audio: '',
},
})

provide('form', form)

const onSubmit = form.handleSubmit((values) => {
  mutateAsync(values as UpdateProductFormData)
})

watch(data, () => {
  form.setValues(data.value as ProductFormData)
})
</script>

<template>
  <Button icon="pi pi-pencil" rounded text size="small" @click="() => visible = true"/>
  <Drawer v-model:visible="visible" header="Edit Product" position="right" class="w-1/2" @show="refresh()">
    <div v-if="isLoading" class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <Skeleton height="1rem" />
        <Skeleton height="3rem" />
      </div>
      <div class="flex flex-col gap-2">
        <Skeleton height="1rem" />
        <Skeleton height="3rem" />
      </div>
      <div class="flex flex-col gap-2">
        <Skeleton height="1rem" />
        <Skeleton height="3rem" />
      </div>
    </div>
    <div v-else class="flex flex-col gap-4">
       <WriteProductDescription :step="2"/>
    </div>
    
    <template #footer>
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
