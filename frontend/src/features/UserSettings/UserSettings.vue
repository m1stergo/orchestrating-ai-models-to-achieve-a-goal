<script setup lang="ts">
import { ref, computed } from 'vue'
import Drawer from 'primevue/drawer'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useQuery, useMutation } from '@pinia/colada'
import { getSettings, updateSettings } from './api'  
import Skeleton from 'primevue/skeleton'

const visible = ref(false)

const { data, isLoading, error } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
  refetchOnWindowFocus: false,
})

const { mutate: updateSettingsMutation } = useMutation({
  mutation: updateSettings,
})

const describe_image_model = computed({
  get: () => data.value?.describe_image_model,
  set: (value) => {
    updateSettingsMutation({ describe_image_model: value })
  }
})

const generate_description_model = computed({
  get: () => data.value?.generate_description_model,
  set: (value) => {
    updateSettingsMutation({ generate_description_model: value })
  }
})


</script>

<template>
  <Button icon="pi pi-cog" label="Settings" severity="secondary" size="small" text @click="() => visible = true" />
  <Drawer 
    v-model:visible="visible" 
    header="Settings" 
    position="right" 
    class="settings-drawer"
    :style="{ width: '50rem' }"
  >
    <div v-if="isLoading" class="flex flex-col gap-2">
      <Skeleton height="2rem"></Skeleton>
      <Skeleton height="2rem"></Skeleton>
      <Skeleton height="2rem"></Skeleton>
      <Skeleton height="2rem"></Skeleton>
    </div>

    <div v-else-if="error" class="error">
      <Message severity="error" :closable="false">
        Error loading models: {{ error.message }}
      </Message>
    </div>
    <div v-else class="flex flex-col gap-4">
      <div>
        <h4>Choose model for image description</h4>
        <div>
          <Dropdown
            id="describe-strategy"
            v-model="describe_image_model"
            :options="data?.describe_image_models"
            placeholder="Select a model"
            class="w-full"
          />
          <small>
            This model will be used to generate image descriptions.
          </small>
        </div>
      </div>

      <div>
        <h4>Choose model for product description</h4>
        <div>
          <Dropdown
            id="generate-strategy"
            v-model="generate_description_model"
            :options="data?.generate_description_models"
            placeholder="Select a model"
            class="w-full"
          />
          <small>
            This model will be used to generate product descriptions.
          </small>
        </div>
      </div>
    </div>
  </Drawer>
</template>