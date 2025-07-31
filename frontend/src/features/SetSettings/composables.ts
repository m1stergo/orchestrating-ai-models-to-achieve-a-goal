import { useQuery, useMutation } from '@pinia/colada'
import { ref } from 'vue'
import type { 
  UserSettingsUpdate,
  SettingsFormData 
} from './types'
import { 
  getAvailableStrategies, 
  getUserSettings, 
  updateUserSettings 
} from './api'

/**
 * Composable for managing available strategies
 */
export function useAvailableStrategies() {
  return useQuery({
    key: ['strategies'],
    query: () => getAvailableStrategies(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

/**
 * Composable for managing user settings
 */
export function useUserSettings(userId: string = 'default') {
  // Query for getting user settings
  const settingsQuery = useQuery({
    key: ['userSettings', userId],
    query: () => getUserSettings(userId),
  })

  // Mutation for updating user settings
  const updateMutation = useMutation({
    mutation: (settings: UserSettingsUpdate) => updateUserSettings(userId, settings),
    onSuccess: () => {
      // Refetch the settings after successful update
      settingsQuery.refetch()
    },
  })

  return {
    // Query state
    settings: settingsQuery.data,
    isLoading: settingsQuery.isLoading,
    error: settingsQuery.error,
    refetch: settingsQuery.refetch,
    
    // Mutation state
    updateSettings: updateMutation.mutate,
    isUpdating: updateMutation.isLoading,
    updateError: updateMutation.error,
  }
}

/**
 * Composable for settings form management
 */
export function useSettingsForm(userId: string = 'default') {
  const { settings, updateSettings, isUpdating, updateError } = useUserSettings(userId)
  const { data: strategies } = useAvailableStrategies()
  
  const formData = ref<SettingsFormData>({
    describe_image_strategy: '',
    generate_description_strategy: '',
  })

  // Initialize form data when settings are loaded
  const initializeForm = () => {
    if (settings.value) {
      formData.value = {
        describe_image_strategy: settings.value.describe_image_strategy,
        generate_description_strategy: settings.value.generate_description_strategy,
      }
    }
  }

  // Submit form data
  const submitForm = async () => {
    if (!formData.value) return
    
    const updateData: UserSettingsUpdate = {
      describe_image_strategy: formData.value.describe_image_strategy,
      generate_description_strategy: formData.value.generate_description_strategy,
    }
    
    await updateSettings(updateData)
  }

  // Reset form to current settings
  const resetForm = () => {
    initializeForm()
  }

  return {
    formData,
    strategies,
    isUpdating,
    updateError,
    initializeForm,
    submitForm,
    resetForm,
  }
}
