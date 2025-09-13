<script setup lang="ts">
import { ref, nextTick, provide } from 'vue'
import Drawer from 'primevue/drawer'
import { WriteProductDescription } from '@/features/WriteProductDescription'
import { useMutation, useQueryCache } from '@pinia/colada'
import { createProduct } from '@/entities/products/api'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import { CreateProductSchema, type CreateProductFormData } from '@/entities/products';

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

const validationSchema = toTypedSchema(CreateProductSchema)

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
  image_description: '',
},
})

provide('form', form)

const onSubmit = form.handleSubmit((values) => {
  mutateAsync(values as CreateProductFormData)
  visible.value = false
})

function onClose() {
  form.resetForm()
}
</script>

<template>
  <Button icon="pi pi-sparkles" label="Write product description" size="small" outlined severity="primary" @click="() => visible = true" />
  <Drawer v-model:visible="visible" header="Write product description" position="right" class="w-1/2" :pt="{ content: { class: 'flex flex-col gap-2' } }" @hide="onClose">
    <WriteProductDescription/>
    <template #footer>
      <Button 
        :disabled="Object.keys(form.errors.value).length > 0" 
        type="submit" 
        label="Submit" 
        class="w-full" 
        @click="onSubmit" 
      />
    </template>
  </Drawer>
</template>
