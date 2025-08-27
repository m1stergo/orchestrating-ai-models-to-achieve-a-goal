<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { EditProduct } from '@/features/EditProduct'
import { DeleteProduct } from '@/features/DeleteProduct'
import { getAllProducts } from '@/entities/products'
import { useQuery } from '@pinia/colada'
import { AudioPlayer } from '@/shared/ui/AudioPlayer'

const { state: products } = useQuery({
  key: ['products'],
  query: getAllProducts,
  refetchOnWindowFocus: false,
})
</script>

<template>
  <DataTable :value="products.data" scrollable scrollHeight="600px">
    <Column field="sku" header="SKU" style="min-width: 120px"></Column>
    <Column field="name" header="Name" style="min-width: 150px" alignFrozen="left" frozen ></Column>
    <Column field="description" header="Description" style="min-width: 200px">
      <template #body="slotProps">
        <div class="max-w-xs truncate" :title="slotProps.data.description">
          {{ slotProps.data.description || 'No description' }}
        </div>
      </template>
    </Column>
    <Column header="Images" style="min-width: 100px">
      <template #body="slotProps">
        <img v-if="slotProps.data.images?.[0]" :src="slotProps.data.images[0]" :alt="slotProps.data.name" class="w-16 h-16 object-cover rounded" />
        <span v-else class="text-gray-400 text-sm">No image</span>
      </template>
    </Column>
    <!-- <Column header="Audio Description" style="min-width: 150px">
      <template #body="slotProps">
        <div v-if="slotProps.data.audio_description" class="max-w-xs truncate" :title="slotProps.data.audio_description">
          {{ slotProps.data.audio_description }}
        </div>
        <span v-else class="text-gray-400 text-sm">No audio description</span>
      </template>
    </Column> -->
    <Column header="Audio" style="min-width: 100px">
      <template #body="slotProps">
        <div v-if="slotProps.data.audio">
          <AudioPlayer :audio="slotProps.data.audio" />
        </div>
        <span v-else class="text-gray-400 text-sm">No audio</span>
      </template>
    </Column>
    <Column field="category" header="Category" style="min-width: 150px"></Column>
    <!-- <Column header="Keywords" style="min-width: 150px">
      <template #body="slotProps">
        <div v-if="slotProps.data.keywords?.length" class="flex flex-wrap gap-1">
          <span v-for="keyword in slotProps.data.keywords.slice(0, 3)" :key="keyword" 
                class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
            {{ keyword }}
          </span>
          <span v-if="slotProps.data.keywords.length > 3" class="text-xs text-gray-500">
            +{{ slotProps.data.keywords.length - 3 }} more
          </span>
        </div>
        <span v-else class="text-gray-400 text-sm">No keywords</span>
      </template>
    </Column> -->
    <Column field="actions" header="Actions" style="min-width: 120px" alignFrozen="right" frozen>
      <template #body="slotProps">    
          <EditProduct v-if="slotProps.data.id" :id="slotProps.data.id" />
          <DeleteProduct v-if="slotProps.data.id" :id="slotProps.data.id" />
      </template>
    </Column>
    <template #empty>
      <slot name="empty" />
    </template>
    <template #footer v-if="products.data?.length"> In total there are {{ products.data?.length || 0 }} products. </template>
  </DataTable>
</template>
