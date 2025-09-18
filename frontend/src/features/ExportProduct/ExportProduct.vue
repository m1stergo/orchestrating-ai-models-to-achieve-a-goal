<script setup lang="ts">
import { useToast } from "primevue/usetoast";
import Button from 'primevue/button'
import { ref } from 'vue'
import { useMutation } from "@pinia/colada";
// Import con type assertion para que TypeScript reconozca el tipo
import { exportProduct } from '@/entities/products/api'
// Traer la definición de ExportResponse - no es necesario exportarla si la usamos sólo aquí
interface ExportResponse {
  filename: string;
  download_url: string;
  size: number;
  products_count: number;
  images_count: number;
  audio_count: number;
}
const props = defineProps<{ id: string }>()
const toast = useToast()
const downloadUrl = ref('')
const { mutate } = useMutation({
  mutation: exportProduct,
  onSuccess: (response) => {
    if (response?.download_url) {
      downloadUrl.value = response.download_url;
      // Abre automáticamente la descarga
      window.open(response.download_url, '_blank');
      toast.add({ severity: 'success', summary: 'Success', detail: 'Product exported successfully. Download started.', life: 3000 });
    } else {
      toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Product exported successfully', life: 3000 });
    }
  },
  onError: (error) => {
    console.error('Export error:', error);
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error exporting the product, please try again', life: 3000 });
  }
})
</script>

<template>
  <Button icon="pi pi-download" rounded text size="small" @click="mutate({ id: props.id })" />
</template>
