<script setup lang="ts">
import FileUpload from 'primevue/fileupload'
import { ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useMutation } from '@pinia/colada'
import { uploadImage } from '@/features/WriteProductDescription/api'

const image = defineModel<string>()

const { isLoading, mutateAsync: triggerUpload } = useMutation({
  mutation: uploadImage,
  onSuccess: (data) => {
    image.value = data.image_url
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error extracting the content, please try again', life: 3000 })
  },
})

const selectedFile = ref<File | null>(null);
const imagePreview = ref('');

const toast = useToast()

const onFileSelect = (event: { files: File[] }) => {
  const file = event.files[0];
  if (file) {
    selectedFile.value = file;
    // Crear una vista previa de la imagen
    const reader = new FileReader();
    reader.onload = (e: ProgressEvent<FileReader>) => {
      if (e.target && e.target.result) {
        imagePreview.value = e.target.result as string;
      }
    };
    reader.readAsDataURL(file);
  }
};

watch(selectedFile, (newFile) => {
  if (!newFile) return;
  const formData = new FormData();
  formData.append('file', newFile);
  triggerUpload(formData)
})
</script>

<template>
<div class="flex flex-col gap-2">
  <div class="flex items-center gap-2">
    <div class="shrink-0">
      <FileUpload :loading="isLoading" :disabled="isLoading" mode="basic" accept="image/*" :maxFileSize="1000000" @select="onFileSelect" :auto="true" chooseLabel="Choose image" class="p-button-outlined"/>
    </div>
    <img v-if="imagePreview" :src="imagePreview" class="rounded shrink-0" alt="Preview" style="width: auto; max-height: 42px;" />
    <p v-if="selectedFile" class="text-sm truncate">{{ selectedFile?.name }}</p>
  </div>
</div>
</template>
