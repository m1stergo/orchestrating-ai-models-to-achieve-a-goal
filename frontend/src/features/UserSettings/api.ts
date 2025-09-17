import type { 
  UserSettingsResponse, 
  UserSettingsUpdate 
} from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

/**
 * Get global application settings
 */
export async function getSettings(): Promise<UserSettingsResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/settings`)
  if (!response.ok) {
    throw new Error(`Failed to get settings: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Update global application settings
 */
export async function updateSettings(settings: UserSettingsUpdate): Promise<UserSettingsResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/settings`, {
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
