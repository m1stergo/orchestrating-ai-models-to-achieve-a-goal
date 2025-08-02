<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import ExtractContentFromWebsite from './ExtractContentFromWebsite.vue'
import UploadImage from './UploadImage.vue'
import type { ExtractWebContentResponse, UploadImageResponse } from './types'
import Skeleton from 'primevue/skeleton'
import { useMutation } from '@pinia/colada'
import { describeImage } from './api'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

const loading = ref(false);

const source = reactive<ExtractWebContentResponse>({
    title: '',
    description: '',
    images: [],
    url: '',
})

const mainImage = computed(() => source.images[0])
const { mutate: describe } = useMutation({
  mutation: describeImage,
  onSuccess: (data) => {
    source.description = data.description
    toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Image described successfully', life: 3000 });
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error describing the image, please try again', life: 3000 });
  },

})

function handleExtractContent(content: ExtractWebContentResponse) {
    source.title = content.title
    source.description = content.description
    source.images = content.images
    source.url = content.url
}

function handleUploadImage(content: UploadImageResponse) {
    source.title = ''
    source.description = ''
    source.images = [content.image_url]
    source.url = ''
}

function handleLoading(isLoading: boolean) {
    loading.value = isLoading
}

watch(mainImage, () => {
    if (mainImage.value) {
        describe(mainImage.value)
    }
})
</script>

<template>
    <Tabs value="0">
        <TabList>
            <Tab value="0">Extract content from website</Tab>
            <Tab value="1">Upload image</Tab>
        </TabList>
        <TabPanels>
            <TabPanel value="0">
                <ExtractContentFromWebsite @update:content="handleExtractContent" @loading="handleLoading" />
            </TabPanel>
            <TabPanel value="1">
                <UploadImage @update:content="handleUploadImage" @loading="handleLoading" />
            </TabPanel>
        </TabPanels>
    </Tabs>
    <div v-if="loading" class="flex flex-col gap-2">
        <div class="flex gap-2">
            <Skeleton size="5rem" v-for="i in 3" :key="i"></Skeleton>
        </div>
        <Skeleton height="2rem"></Skeleton>
        <Skeleton height="4rem"></Skeleton>
    </div>
</template>
