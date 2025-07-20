<script setup lang="ts">
import { ProductsTable } from '@/widgets/ProductsTable'
import { CreateProduct } from '@/features/CreateProduct'
import Toast from 'primevue/toast'
</script>

<template>
  <Toast position="top-center"/>
  <main>
    <ProductsTable>
      <template #header>
        <CreateProduct />
      </template>
    </ProductsTable>
  </main>
</template>
