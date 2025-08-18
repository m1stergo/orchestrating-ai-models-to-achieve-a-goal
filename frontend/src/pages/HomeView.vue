<script setup lang="ts">
import ProductsTable from './ProductsTable.vue'
import { CreateProduct } from '@/features/CreateProduct'
import Toolbar from 'primevue/toolbar'
import { UserSettings } from '@/features/UserSettings'
</script>

<template>
<Toolbar>
    <template #start>
    <h1 class="font-bold">Product description generator</h1>
    </template>

    <template #end>
      <CreateProduct />
      <UserSettings />
    </template>
</Toolbar>
  <main class="p-4 h-full">
    <ProductsTable class="rounded-lg overflow-hidden bg-white flex flex-col">
      <template #empty>
        <div class="flex flex-col items-center justify-center h-full gap-4 min-h-[400px]">
          <p class="text-gray-500">You haven't created any products yet.</p>
          <CreateProduct />
        </div>
      </template>
    </ProductsTable>
  </main>
</template>
