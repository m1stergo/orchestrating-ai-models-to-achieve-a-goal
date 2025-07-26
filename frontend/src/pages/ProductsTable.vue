<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { EditProduct } from '@/features/EditProduct'
import { DeleteProduct } from '@/features/DeleteProduct'
import { getAllProducts } from '@/entities/products'
import { useQuery } from '@pinia/colada'
const { state: products } = useQuery({
  key: ['products'],
  query: getAllProducts,
})
</script>

<template>
  <DataTable :value="products.data" tableStyle="min-width: 50rem">
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span class="text-xl font-bold">Products</span>
        <slot name="header" />
      </div>
    </template>
    <Column field="name" header="Name"></Column>
    <Column header="Images">
      <template #body="slotProps">
        <img :src="slotProps.data.images[0]" :alt="slotProps.data.images[0]" class="w-24 rounded" />
      </template>
    </Column>
    <Column field="description" header="Description"></Column>
    <Column field="actions" header="Actions">
      <template #body="slotProps">    
          <EditProduct v-if="slotProps.data.id" :id="slotProps.data.id" />
          <DeleteProduct v-if="slotProps.data.id" :id="slotProps.data.id" />
      </template>
    </Column>
    <template #footer> In total there are {{ products.data?.length || 0 }} products. </template>
  </DataTable>
</template>
