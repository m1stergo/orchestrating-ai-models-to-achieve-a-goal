<script setup lang="ts">
import { ref, nextTick } from 'vue'

import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
import { DescribeImage } from '@/features/DescribeImage'
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

const name = ref('')
const description = ref('')
const images = ref<string[]>([])
const audio = ref('')

const handleSubmit = async () => {
  await mutateAsync({
    name: name.value || 'prueba',
    description: description.value || 'prueba',
    images: images.value || ['prueba'],
    audio: audio.value || 'prueba',
  })
  visible.value = false
}
</script>

<template>
  <Button label="Add product" rounded text size="small" @click="() => visible = true"/>
  <Drawer v-model:visible="visible" header="Create Product" position="right" class="w-1/2">
    <DescribeImage />
    <WriteProductDescription />
    <Button type="submit" label="Submit" @click="handleSubmit" />
  </Drawer>
</template>
