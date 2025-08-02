<script setup lang="ts">
import { ref, nextTick, reactive, watch } from 'vue'

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

const product: ProductUpdate = reactive({
  id: props.id,
  name: '',
  description: '',
  images: [],
  audio: '',
})


const handleSubmit = async () => {
  await mutateAsync({
    id: props.id,
    name: product.name,
    description: product.description,
    images: product.images,
    audio: product.audio,
  })
  visible.value = false
}

watch(data, () => {
  if (data.value) {
    product.name = data.value.name
    product.description = data.value.description
    product.images = data.value.images
    product.audio = data.value.audio
  }
})
</script>

<template>
  <Button icon="pi pi-pencil" rounded text size="small" @click="() => visible = true"/>
  <Drawer v-model:visible="visible" header="Edit Product" position="right" class="w-1/2" @show="refresh()">
    {{ isLoading }}
    <div class="prose">
      <InputText v-model="product.name" placeholder="Name" />
      <WriteProductDescription />
    </div>
    <Button type="submit" label="Submit" @click="handleSubmit" />
  </Drawer>
</template>
