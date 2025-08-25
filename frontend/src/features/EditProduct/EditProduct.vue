<script setup lang="ts">
import { ref, nextTick, reactive, watch, computed } from 'vue'

import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
import { WriteProductDescription } from '@/features/WriteProductDescription'
import { useMutation, useQueryCache, useQuery } from '@pinia/colada'
import { updateProduct, getProductById } from '@/entities/products/api'
import { useToast } from 'primevue/usetoast'
import InputText from 'primevue/inputtext'
import type { ProductUpdate } from '@/entities/products/types'

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

const product = ref<ProductUpdate>({
  id: props.id,
  name: '',
  sku: '',
  description: '',
  keywords: [],
  category: '',
  images: [],
  audio_description: '',
  audio: '',
})


const handleSubmit = async () => {
  await mutateAsync({
    id: props.id,
    name: product.value.name,
    sku: product.value.sku,
    description: product.value.description,
    keywords: product.value.keywords,
    category: product.value.category,
    images: product.value.images,
    audio_description: product.value.audio_description,
    audio: product.value.audio,
  })
  visible.value = false
}

watch(data, () => {
  if (data.value) {
    product.value = data.value
  }
})
</script>

<template>
  <Button icon="pi pi-pencil" rounded text size="small" @click="() => visible = true"/>
  <Drawer v-model:visible="visible" header="Edit Product" position="right" class="w-1/2" @show="refresh()">
    <div v-if="isLoading" class="flex justify-center p-4">
      Loading product data...
    </div>
    <div v-else class="flex flex-col gap-4">
      <WriteProductDescription v-model="product" />
      <Button 
        :disabled="!product.name || !product.description" 
        type="submit" 
        label="Update Product" 
        @click="handleSubmit" 
      />
    </div>
  </Drawer>
</template>
