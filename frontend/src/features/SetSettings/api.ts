import type { 
  AvailableStrategiesResponse, 
  UserSettingsResponse, 
  UserSettingsCreate, 
  UserSettingsUpdate 
} from './types'

const BASE_URL = 'http://localhost:8000/api/v1/settings'

/**
 * Get available strategies for both services
 */
export async function getAvailableStrategies(): Promise<AvailableStrategiesResponse> {
  const response = await fetch(`${BASE_URL}/strategies`)
  if (!response.ok) {
    throw new Error(`Failed to get available strategies: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Get user settings by user ID
 */
export async function getUserSettings(userId: string = 'default'): Promise<UserSettingsResponse> {
  const response = await fetch(`${BASE_URL}/${userId}`)
  if (!response.ok) {
    throw new Error(`Failed to get user settings: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Create new user settings
 */
export async function createUserSettings(settings: UserSettingsCreate): Promise<UserSettingsResponse> {
  const response = await fetch(`${BASE_URL}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(settings),
  })
  if (!response.ok) {
    throw new Error(`Failed to create user settings: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Update user settings
 */
export async function updateUserSettings(
  userId: string, 
  settings: UserSettingsUpdate
): Promise<UserSettingsResponse> {
  const response = await fetch(`${BASE_URL}/${userId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(settings),
  })
  if (!response.ok) {
    throw new Error(`Failed to update user settings: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Delete user settings
 */
export async function deleteUserSettings(userId: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/${userId}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(`Failed to delete user settings: ${response.statusText}`)
  }
}
