<script setup lang="ts">
import { computed, ref } from 'vue'
import Drawer from 'primevue/drawer'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import { useUserSettings, useSettingsForm } from './composables'
import { useQuery } from '@pinia/colada'
import { getAvailableStrategies } from './api'  

const visible = ref(true)

const { data: strategies, isLoading: isLoadingStrategies, error: errorStrategies } = useQuery({
  key: ['strategies'],
  query: () => getAvailableStrategies(),
})

// const visible = computed({
//   get: () => props.visible,
//   set: (value) => emit('update:visible', value)
// })

// Use the existing composables
// const { settings, isLoading, error } = useUserSettings(props.userId)
// const { 
//   formData, 
//   strategies, 
//   isUpdating: isSaving, 
//   initializeForm,
//   submitForm: handleSubmit,
//   resetForm: handleReset
// } = useSettingsForm(props.userId)

// // Create options from strategies
// const describeImageOptions = computed(() => {
//   if (!strategies.value?.describe_image_strategies) return []
//   return strategies.value.describe_image_strategies.map((strategy) => ({
//     label: strategy.name,
//     value: strategy.name
//   }))
// })

// const generateDescriptionOptions = computed(() => {
//   if (!strategies.value?.generate_description_strategies) return []
//   return strategies.value.generate_description_strategies.map((strategy) => ({
//     label: strategy.name,
//     value: strategy.name
//   }))
// })

// Initialize form when settings are loaded
// watch(() => settings.value, (newSettings: any) => {
//   if (newSettings) {
//     initializeForm()
//   }
// }, { immediate: true })
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
    <div v-if="isLoadingStrategies" class="loading">
      <ProgressSpinner />
      <p>Loading models...</p>
    </div>

    <div v-else-if="errorStrategies" class="error">
      <Message severity="error" :closable="false">
        Error loading models: {{ errorStrategies.message }}
      </Message>
    </div>

    <!-- <form v-else @submit.prevent="handleSubmit" class="settings-form">
      <div class="form-section">
        <h4>Choose model for image description</h4>
        <div class="field">
          <Dropdown
            id="describe-strategy"
            v-model="formData.describe_image_strategy"
            :options="describeImageOptions"
            option-label="label"
            option-value="value"
            placeholder="Select a model"
            class="w-full"
          />
          <small class="field-help">
            This model will be used to generate image descriptions.
          </small>
        </div>
      </div>

      <div class="form-section">
        <h4>Choose model for product description</h4>
        <div class="field">
          <Dropdown
            id="generate-strategy"
            v-model="formData.generate_description_strategy"
            :options="generateDescriptionOptions"
            option-label="label"
            option-value="value"
            placeholder="Select a model"
            class="w-full"
          />
          <small class="field-help">
            This model will be used to generate product descriptions.
          </small>
        </div>
      </div>

      <div class="form-actions">
        <Button 
          type="button" 
          label="Reset" 
          severity="secondary" 
          @click="handleReset"
          :disabled="isSaving"
        />
        <Button 
          type="submit" 
          label="Save Settings" 
          :loading="isSaving"
        />
      </div>
    </form> -->
  </Drawer>
</template>