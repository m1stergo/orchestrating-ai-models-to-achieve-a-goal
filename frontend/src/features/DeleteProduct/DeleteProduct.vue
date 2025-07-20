<script setup lang="ts">
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import Button from 'primevue/button'
import ConfirmPopup from 'primevue/confirmpopup'
import { useMutation, useQueryCache } from "@pinia/colada";
import { deleteProduct } from '@/entities/products/api'
const confirm = useConfirm();
const props = defineProps<{ id: number }>()
const queryCache = useQueryCache()
const toast = useToast()
const { mutate } = useMutation({
  mutation: deleteProduct,
  onSettled: async () => {
    await queryCache.invalidateQueries({ key: ['products'], exact: true })
    toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Product deleted successfully', life: 3000 });
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error deleting the product, please try again', life: 3000 });
  }
})

const handleDelete = (event: any) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this product?',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      outlined: true
    },
    acceptProps: {
      label: 'Delete',
      severity: 'danger',
    },
    accept: () => {
      mutate(props.id)
    },
  });
}
</script>

<template>
  <ConfirmPopup></ConfirmPopup>
  <Button icon="pi pi-trash" rounded text size="small" @click="handleDelete($event)" />
</template>
