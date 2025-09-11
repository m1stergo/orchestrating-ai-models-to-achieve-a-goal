const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export type DescribeImageWarmupParams = {
    model: string
}

type DescribeImageStatusParams = {
  model: string,
  job_id: string
}

export type DescribeImageInferenceParams = {
  model: string,
  image_url: string,
  prompt?: string
}

export interface ExtractWebContentRequest {
  url: string
}

export interface ExtractWebContentResponse {
  title: string
  url: string
  description: string
  images: string[]
}

export interface UploadImageResponse {
  image_url: string
  filename: string
  content_type: string
  size: number
}

export interface UploadAudioResponse {
  audio_url: string
  filename: string
}

export interface VoiceModel {
  name: string
  audio_url: string
}

export interface VoiceModelsResponse {
  voices: VoiceModel[]
  count: number
}

export interface ServiceResponse<T> {
  status: string
  message: string
  data?: T
}

export interface TextToSpeechResponse {
  audio_url: string
}

export enum Status {
  PENDING = 'pending',
  SUCCESS = 'success',
  ERROR = 'error'
}

export interface StatusResponse {
  status: string
  job_status?: string
  message?: string
  http_status?: number
  status_code?: number
  detail?: any
}

export async function warmup(service: string, params: DescribeImageWarmupParams): Promise<ServiceResponse<string>> {
  const response = await fetch(`${API_BASE_URL}/v1/${service}/warmup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params)
  })
  if (!response.ok) {
    throw new Error(`Failed to warmup ${service} model ${params.model}: ${response.statusText}`)
  }
  const data = await response.json()
  if (data.status === 'error') {
    throw new Error(data.message)
  }
  return data
}

export async function status(service: string, params: DescribeImageStatusParams): Promise<ServiceResponse<string>> {
  const response = await fetch(`${API_BASE_URL}/v1/${service}/status`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params)
  })
  if (!response.ok) {
    throw new Error(`Failed to get status of ${service} model ${params.model}: ${response.statusText}`)
  }
  const data = await response.json()
  if (data.status === 'error') {
    throw new Error(data.message)
  }
  return data
}

export async function inference(service: string, params: DescribeImageInferenceParams): Promise<ServiceResponse<string>> {
    const response = await fetch(`${API_BASE_URL}/v1/${service}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_url: params.image_url,
        prompt: params.prompt,
        model: params.model
      })
    })
    if (!response.ok) {
      throw new Error(`Failed to ${service} model ${params.model}: ${response.statusText}`)
    }
    const data = await response.json()
    if (data.status === 'error') {
      throw new Error(data.message)
    }
    return data
}

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

export async function generatePromotionalAudioScript(params: { text: string, model: string, prompt?: string }): Promise<ServiceResponse<string>> {
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