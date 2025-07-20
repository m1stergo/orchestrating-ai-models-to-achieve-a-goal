<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import { ref } from 'vue'

const name = ref('')
const description = ref('')

const handleSubmit = () => {
  console.log(name.value, description.value)
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
            <InputText v-model="name" placeholder="Url" />
            <Button label="Go" @click="handleSubmit" />
          </div>
        </TabPanel>
        <TabPanel value="1">
          <div class="flex gap-2">
            <InputText v-model="description" placeholder="File" />
            <Button label="Go" @click="handleSubmit" />
          </div>
        </TabPanel>
    </TabPanels>
  </Tabs>
</template>
