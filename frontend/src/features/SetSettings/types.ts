/**
 * Types for user settings management
 */

/**
 * Strategy information
 */
export interface StrategyInfo {
  name: string
  type: string
  provider: string
  description: string
}

/**
 * Available strategies response from backend
 */
export interface AvailableStrategiesResponse {
  describe_image_strategies: StrategyInfo[]
  generate_description_strategies: StrategyInfo[]
}

/**
 * User settings base structure
 */
export interface UserSettingsBase {
  user_id: string
  describe_image_strategy: string
  generate_description_strategy: string
}

/**
 * User settings for creation
 */
export interface UserSettingsCreate extends UserSettingsBase {}

/**
 * User settings for updates (all fields optional)
 */
export interface UserSettingsUpdate {
  describe_image_strategy?: string
  generate_description_strategy?: string
}

/**
 * User settings response from backend
 */
export interface UserSettingsResponse extends UserSettingsBase {
  id: number
  created_at: string
  updated_at: string
}

/**
 * Settings form data for the UI
 */
export interface SettingsFormData {
  describe_image_strategy: string
  generate_description_strategy: string
}
