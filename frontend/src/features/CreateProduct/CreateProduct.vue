<script setup lang="ts">
import { ref, nextTick, reactive } from 'vue'

import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
import { WriteProductDescription } from '@/features/WriteProductDescription'
import { useMutation, useQueryCache } from '@pinia/colada'
import { createProduct } from '@/entities/products/api'
import { useToast } from 'primevue/usetoast'
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

const visible = ref(false)

const product = reactive({
  name: '',
  description: '',
  images: [],
  audio: '',
})

const handleSubmit = async () => {
  await mutateAsync({
    name: product.name || 'prueba',
    description: product.description || 'prueba',
    images: product.images || ['prueba'],
    audio: product.audio || 'prueba',
  })
  visible.value = false
}
</script>

<template>
  <Button label="Write product description" rounded text size="small" @click="() => visible = true" />
  <Drawer v-model:visible="visible" header="Write product description" position="right" class="w-1/2" :pt="{ content: { class: 'flex flex-col gap-2' } }">
    <WriteProductDescription v-model="product" />
    <Button type="submit" label="Submit" @click="handleSubmit" class="mt-auto" />
  </Drawer>
</template>
