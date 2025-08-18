/**
 * Types for web content extraction
 */

/**
 * Schema for web content extraction request.
 */
export interface ExtractWebContentRequest {
  url: string
}

/**
 * Schema for web content extraction response.
 */
export interface ExtractWebContentResponse {
  url: string
  title: string
  description: string
  images: string[]
}

export interface UploadImageResponse {
  image_url: string
  filename: string
  content_type: string
  size: number
}

export interface DescribeImageResponse {
  description: string 
}

export interface UploadAudioResponse {
  audio_url: string
  filename: string
}

export interface GenerateDescriptionResponse {
  description: string
}

export interface VoiceModel {
  name: string
  audio_url: string
}

export interface VoiceModelsResponse {
  voices: VoiceModel[]
  count: number
}

export interface GenerateReelResponse {
  text: string
}

export interface TextToSpeechResponse {
  audio_url: string
}
