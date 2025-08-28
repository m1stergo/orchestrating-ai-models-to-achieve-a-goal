<script setup lang="ts">
import { ref, computed } from 'vue'
import Drawer from 'primevue/drawer'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Textarea from 'primevue/textarea'
import AutoComplete from 'primevue/autocomplete'
import { useQuery, useMutation, useQueryCache } from '@pinia/colada'
import { getSettings, updateSettings } from './api'  
import Skeleton from 'primevue/skeleton'
import { type UserSettingsResponse } from './types'

const visible = ref(false)

const queryCache = useQueryCache()

const { data, isLoading, error } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
  refetchOnWindowFocus: false,
})

// const localData = ref<UserSettingsResponse | null>(null);

const { mutate: updateSettingsMutation } = useMutation({
  mutation: updateSettings,
  onMutate: (newSettings) => {
    const oldSettings = queryCache.getQueryData<UserSettingsResponse>(['settings'])!
    queryCache.setQueryData(['settings'], {...oldSettings, ...newSettings})
    queryCache.cancelQueries({ key: ['settings'] })

    return { oldSettings, newSettings }
  },
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

const describe_image_prompt = computed({
  get: () => data.value?.describe_image_prompt,
  set: (value) => {
    updateSettingsMutation({ describe_image_prompt: value })
  }
})

const generate_description_prompt = computed({
  get: () => data.value?.generate_description_prompt,
  set: (value) => {
    updateSettingsMutation({ generate_description_prompt: value })
  }
})

const generate_promotional_audio_script_prompt = computed({
  get: () => data.value?.generate_promotional_audio_script_prompt,
  set: (value) => {
    updateSettingsMutation({ generate_promotional_audio_script_prompt: value })
  }
})

const categories = computed({
  get: () => data.value?.categories,
  set: (value) => {
    updateSettingsMutation({ categories: value })
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
    :style="{ width: '60rem' }"
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
    <div v-else class="flex flex-col gap-6">
      <!-- AI Models Section -->
      <div class="pb-4">
        <h3 class="text-lg font-semibold mb-4">AI Models</h3>
        
        <div class="flex flex-col gap-4">
          <div>
            <label class="block text-sm font-medium mb-2">Image Description Model</label>
            <Dropdown
              id="describe-strategy"
              v-model="describe_image_model"
              :options="data?.describe_image_models"
              placeholder="Select a model"
              class="w-full"
            />
            <small class="text-gray-600">
              This model will be used to generate image descriptions.
            </small>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">Product Description Model</label>
            <Dropdown
              id="generate-strategy"
              v-model="generate_description_model"
              :options="data?.generate_description_models"
              placeholder="Select a model"
              class="w-full"
            />
            <small class="text-gray-600">
              This model will be used to generate product descriptions.
            </small>
          </div>
        </div>
      </div>

      <!-- Prompts Section -->
      <div class="pb-4">
        <h3 class="text-lg font-semibold mb-4">Custom Prompts</h3>
        
        <div class="flex flex-col gap-4">
          <div>
            <label class="block text-sm font-medium mb-2">Image Description Prompt</label>
            <Textarea
              v-model="describe_image_prompt"
              placeholder="Enter custom prompt for image description generation..."
              rows="3"
              class="w-full"
              autoResize
              debounce="300"
            />
            <small class="text-gray-600">
              Prompt template for describing images.  
            </small>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">Product Description Prompt</label>
            <Textarea
              v-model="generate_description_prompt"
              placeholder="Enter custom prompt for product description generation..."
              rows="3"
              class="w-full"
              autoResize
              debounce="300"
            />
            <small class="text-gray-600">
              Prompt template for generating product descriptions.
            </small>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">Promotional Audio Script Prompt</label>
            <Textarea
              v-model="generate_promotional_audio_script_prompt"
              placeholder="Enter custom prompt for promotional audio script generation..."
              rows="3"
              class="w-full"
              autoResize
              debounce="300"
            />
            <small class="text-gray-600">
              Prompt template for generating promotional audio scripts.
            </small>
          </div>
        </div>
      </div>

      <!-- Product Management Section -->
      <div class="pb-4">
        <h3 class="text-lg font-semibold mb-4">Product Management</h3>
        
        <div class="flex flex-col gap-4">
          <div>
            <label class="block text-sm font-medium mb-2">Product Categories</label>
            <AutoComplete
              v-model="categories"
              multiple
              placeholder="Add categories..."
              class="w-full"
              :typeahead="false"
            />
            <small class="text-gray-600">
              Define the available product categories for the organization. These will be used to infer the category from the product descriptions.
            </small>
          </div>
        </div>
      </div>

    </div>
  </Drawer>
</template>