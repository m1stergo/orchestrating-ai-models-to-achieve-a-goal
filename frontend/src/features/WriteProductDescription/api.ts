import type { ExtractWebContentRequest, ExtractWebContentResponse, UploadImageResponse, ServiceResponse, VoiceModelsResponse, TextToSpeechResponse, StatusResponse } from './types'

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

export async function describeImage(params: { image_url: string, model?: string, prompt?: string }): Promise<ServiceResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/describe-image/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  })
  if (!response.ok) {
    // Get the error detail from the response body
    const errorData = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(errorData.detail || `Failed to describe image: ${response.statusText}`)
  }
  return response.json()
}

export async function generateDescription(params: { text: string, model: string, prompt?: string, categories?: string[] }): Promise<ServiceResponse> {
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

export async function generatePromotionalAudioScript(params: { text: string, model: string, prompt?: string }): Promise<ServiceResponse> {
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

// Nuevos endpoints para status y warmup
export async function describeImageWarmup(model: string): Promise<StatusResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/describe-image/warmup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ model }),
  })
  if (!response.ok) {
    throw new Error(`Failed to warmup describe image model: ${response.statusText}`)
  }
  return response.json()
}

export async function describeImageStatus(params: { model: string, job_id?: string }): Promise<StatusResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/describe-image/status`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  })
  
  // No throw error here to handle different status codes in the caller
  return response.json()
}