<script setup lang="ts">
import { ref, reactive } from 'vue'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import Card from 'primevue/card'
import Chip from 'primevue/chip';
import ExtractContentFromWebsite from './ExtractContentFromWebsite.vue'
import UploadImage from './UploadImage.vue'
import type { ExtractSiteContentResponse, UploadImageResponse } from '../DescribeImage/types'
import Skeleton from 'primevue/skeleton'

const loading = ref(false);
const product = defineModel()

const source = reactive<ExtractSiteContentResponse>({
    title: '',
    description: '',
    keywords: [],
    images: [],
    url: '',
})

function handleExtractContent(content: ExtractSiteContentResponse) {
    source.title = content.title
    source.description = content.description
    source.keywords = content.keywords
    source.images = content.images
    source.url = content.url
}

function handleUploadImage(content: UploadImageResponse) {
    source.title = ''
    source.description = ''
    source.keywords = []
    source.images = [content.image_url]
    source.url = ''
}

function handleLoading(isLoading: boolean) {
    loading.value = isLoading
}
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
    <div v-else>
        <div v-if="source.images.length > 0" class="flex gap-2">
            <img v-for="image in source.images" :key="image" :src="image" :alt="image" class="w-24 rounded" />
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
