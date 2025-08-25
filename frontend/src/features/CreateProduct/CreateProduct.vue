<script setup lang="ts">
import { ref, nextTick } from 'vue'
import Drawer from 'primevue/drawer'
import { WriteProductDescription } from '@/features/WriteProductDescription'
import { useMutation, useQueryCache } from '@pinia/colada'
import { createProduct } from '@/entities/products/api'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import type { ProductCreate } from '@/entities/products/types'

const queryCache = useQueryCache()

const toast = useToast()
const {
  mutateAsync,
} = useMutation({
  mutation: createProduct,
  onSettled: async () => {
    await queryCache.invalidateQueries({ key: ['products'], exact: true })
    nextTick(() => {
      toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Product created successfully', life: 3000 });
    })
  },
  onError: () => {
    nextTick(() => {
      toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error creating the product, please try again', life: 3000 });
    })
  }
})

const visible = ref(true)

const product = ref<ProductCreate>({
  name: 'Untitled Product',
  sku: '',
  description: '',
  keywords: [],
  category: '',
  images: [],
  audio_description: '',
  audio: '',
})

const handleSubmit = async () => {
  await mutateAsync(product.value)
  visible.value = false
}
</script>

<template>
  <Button icon="pi pi-sparkles" label="Write product description" size="small" outlined severity="primary" @click="() => visible = true" />
  <Drawer v-model:visible="visible" header="Write product description" position="right" class="w-1/2" :pt="{ content: { class: 'flex flex-col gap-2' } }">
    <WriteProductDescription v-model="product" />
    <Button 
      :disabled="!product.name || !product.description" 
      type="submit" 
      label="Submit" 
      @click="handleSubmit" 
      class="mt-auto" 
    />
  </Drawer>
</template>
