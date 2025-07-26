<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import FileUpload from 'primevue/fileupload'
import { ref, toRef } from 'vue'
import { useMutation } from '@pinia/colada'
import { describeImage, extractSiteContent } from './api'
import { useToast } from 'primevue/usetoast'


const props = defineProps<{
    image: string,
}>()

const image = toRef(props.image)

const toast = useToast()



</script>

<template>
  <div>
    <div v-if="image" class="flex gap-2">
        <img :src="image" :alt="image" class="w-24 rounded" />
    </div>
    <div v-else>
        <p>No images available</p>
    </div>
    <div class="flex gap-2">
        <span>Keywords:</span>
        <Chip v-for="keyword in source.keywords" :key="keyword" :label="keyword" />
    </div>
    <h4>Title</h4>
    <p>{{ source.title }}</p>
    <h4>Description</h4>
    <p>{{ source.description }}</p>
  </div>
</template>
