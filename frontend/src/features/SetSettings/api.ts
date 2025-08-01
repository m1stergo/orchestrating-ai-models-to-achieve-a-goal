import type { 
  AvailableModelsResponse, 
  UserSettingsResponse, 
  UserSettingsCreate, 
  UserSettingsUpdate 
} from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const BASE_URL = `${API_BASE_URL}/api/v1/settings`

/**
 * Get available models for both services
 */
export async function getAvailableModels(): Promise<AvailableModelsResponse> {
  const response = await fetch(`${BASE_URL}/models`)
  if (!response.ok) {
    throw new Error(`Failed to get available models: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Get global application settings
 */
export async function getSettings(): Promise<UserSettingsResponse> {
  const response = await fetch(`${BASE_URL}/`)
  if (!response.ok) {
    throw new Error(`Failed to get settings: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Update global application settings
 */
export async function updateSettings(settings: UserSettingsUpdate): Promise<UserSettingsResponse> {
  const response = await fetch(`${BASE_URL}/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(settings),
  })
  if (!response.ok) {
    throw new Error(`Failed to update settings: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Reset settings to default values
 */
export async function resetSettings(): Promise<UserSettingsResponse> {
  const response = await fetch(`${BASE_URL}/reset`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error(`Failed to reset settings: ${response.statusText}`)
  }
  return response.json()
}
