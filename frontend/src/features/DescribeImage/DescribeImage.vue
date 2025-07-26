<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import FileUpload from 'primevue/fileupload'
import { ref } from 'vue'
import { useMutation } from '@pinia/colada'
import { describeImage, extractSiteContent } from './api'
import { useToast } from 'primevue/usetoast'

const siteUrl = ref('')
const selectedFile = ref<File | null>(null);
const imagePreview = ref('');

const toast = useToast()

// Función para manejar la selección de archivos
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

// Función para subir la imagen al backend
const uploadImage = async () => {
  if (!selectedFile.value) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Por favor selecciona una imagen', life: 3000 });
    return;
  }
  
  try {
    // Crear un FormData para enviar el archivo
    const formData = new FormData();
    formData.append('file', selectedFile.value);
    
    // Llamar a la API de backend para subir la imagen
    const response = await fetch('http://localhost:8000/api/v1/upload-image/', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Error al subir la imagen: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    // Usar la URL de la imagen subida para describir la imagen
    // await describe(result.image_url);
    
    toast.add({ severity: 'success', summary: 'Éxito', detail: 'Imagen subida correctamente', life: 3000 });
  } catch (error: unknown) {
    console.error('Error al subir la imagen:', error);
    const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
    toast.add({ severity: 'error', summary: 'Error', detail: `Error al subir la imagen: ${errorMessage}`, life: 3000 });
  }
};

const { mutateAsync: describe } = useMutation({
  mutation: describeImage,
  onSuccess: (data) => {
    toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Image described successfully', life: 3000 });
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error describing the image, please try again', life: 3000 });
  },
})


const { mutateAsync: extract } = useMutation({
  mutation: extractSiteContent,
  onSuccess: (data) => {
    console.log(data);
    toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Content extracted successfully', life: 3000 });
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error extracting the content, please try again', life: 3000 });
  },
})

const handleSubmit = () => {

}


</script>

<template>
  <h2>Describe Image</h2>
  <Tabs value="0">
    <TabList>
        <Tab value="0">From url</Tab>
        <Tab value="1">From file</Tab>
    </TabList>
    <TabPanels>
        <TabPanel value="0">
          <div class="flex gap-2">
            <InputText v-model="siteUrl" placeholder="Url" />
            <Button label="Go" @click="extract(siteUrl)" />
          </div>
        </TabPanel>
        <TabPanel value="1">
          <div class="flex flex-column gap-2">
            <div class="flex gap-2">
              <FileUpload mode="basic" accept="image/*" :maxFileSize="1000000" @select="onFileSelect" :auto="true" chooseLabel="Choose image"/>
              <Button label="Upload" @click="uploadImage" severity="primary" :disabled="!selectedFile" />
            </div>
          </div>
          <div v-if="imagePreview" class="mt-3">
            <img :src="imagePreview" alt="Preview" style="max-width: 300px; max-height: 300px;" />
          </div>
        </TabPanel>
    </TabPanels>
  </Tabs>
</template>
