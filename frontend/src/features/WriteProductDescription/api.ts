import type { ExtractWebContentRequest, ExtractWebContentResponse, UploadImageResponse, DescribeImageResponse, GenerateDescriptionResponse, VoiceModelsResponse, GeneratePromotionalAudioScriptResponse, TextToSpeechResponse } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export async function uploadImage(formData: FormData): Promise<UploadImageResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/upload-image/`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) {
    throw new Error(`Failed to upload image: ${response.statusText}`)
  }
  return response.json()
}

export async function describeImage(params: { image_url: string, model: string }): Promise<DescribeImageResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/describe-image/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  })
  if (!response.ok) {
    throw new Error(`Failed to describe image: ${response.statusText}`)
  }
  return response.json()
}

export async function generateDescription(params: { text: string, model: string }): Promise<GenerateDescriptionResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/generate-description/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  })
  if (!response.ok) {
    throw new Error(`Failed to generate description: ${response.statusText}`)
  }
  return response.json()
}

export async function extractWebContent(url: string): Promise<ExtractWebContentResponse> {
  let formattedUrl = url;
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    formattedUrl = `https://${url}`;
  }
  
  const request: ExtractWebContentRequest = { url: formattedUrl }
  
  const response = await fetch(`${API_BASE_URL}/v1/extract-webcontent/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  
  if (!response.ok) {
    throw new Error(`Failed to extract content: ${response.statusText}`)
  }

  return response.json() as Promise<ExtractWebContentResponse>
}

export async function getAvailableVoices(): Promise<VoiceModelsResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/text-to-speech/voices`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  if (!response.ok) {
    throw new Error(`Failed to get available voices: ${response.statusText}`)
  }
  return response.json()
}

export async function generatePromotionalAudioScript(params: { text: string, model: string }): Promise<GeneratePromotionalAudioScriptResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/generate-description/promotional-audio-script`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  })
  if (!response.ok) {
    throw new Error(`Failed to generate promotional audio script: ${response.statusText}`)
  }
  return response.json()
}

export async function generateTextToSpeech(params: { text: string, model?: string, audio_prompt_url?: string }): Promise<TextToSpeechResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/text-to-speech/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  })
  if (!response.ok) {
    throw new Error(`Failed to generate text to speech: ${response.statusText}`)
  }
  return response.json()
}
