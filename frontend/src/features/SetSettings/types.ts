/**
 * Types for user settings management
 *

/**
 * User settings base structure
 */
export interface UserSettingsBase {
  describe_image_model: string
  generate_description_model: string
  describe_image_models: string[]
  generate_description_models: string[]
}

/**
 * User settings for creation
 */
export interface UserSettingsCreate extends UserSettingsBase {}

/**
 * User settings for updates (all fields optional)
 */
export interface UserSettingsUpdate {
  describe_image_model?: string
  generate_description_model?: string
}

/**
 * User settings response from backend
 */
export interface UserSettingsResponse extends UserSettingsBase {
  id: number
  created_at: string
  updated_at: string
}
