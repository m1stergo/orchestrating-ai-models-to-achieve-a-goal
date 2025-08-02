<script setup lang="ts">
import { ref } from 'vue'
import { useMutation } from '@pinia/colada'
import { extractWebContent } from '@/features/WriteProductDescription/api'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
const toast = useToast()
const siteUrl = ref('')
const emit = defineEmits(['update:content', 'loading'])
const { isLoading, mutateAsync: extract } = useMutation({
  mutation: extractWebContent,
  onSuccess: (data) => {
    emit('update:content', data)
    emit('loading', false)
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error extracting the content, please try again', life: 3000 })
    emit('loading', false)
  },
})
const handleSubmit = () => {
  emit('loading', true)
  extract(siteUrl.value)
}
</script>

<template>
  <div class="flex gap-2">
    <InputText v-model="siteUrl" placeholder="Url" class="w-full" :disabled="isLoading"/>
    <Button label="Go" @click="handleSubmit" :disabled="isLoading" />
  </div>
</template>