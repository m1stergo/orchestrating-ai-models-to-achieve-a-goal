import type { ExtractWebContentRequest, ExtractWebContentResponse, UploadImageResponse, DescribeImageResponse } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
const API_DESCRIBE_IMAGE_URL = import.meta.env.VITE_API_DESCRIBE_IMAGE_URL
const API_EXTRACT_WEBCONTENT_URL = import.meta.env.VITE_API_BASE_URL

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

export async function describeImage(image: string): Promise<DescribeImageResponse> {
  const response = await fetch(`${API_DESCRIBE_IMAGE_URL}/v1/describe-image/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ image }),
  })
  if (!response.ok) {
    throw new Error(`Failed to describe image: ${response.statusText}`)
  }
  return response.json()
}

export async function extractWebContent(url: string): Promise<ExtractWebContentResponse> {
  let formattedUrl = url;
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    formattedUrl = `https://${url}`;
  }
  
  const request: ExtractWebContentRequest = { url: formattedUrl }
  
  const response = await fetch(`${API_EXTRACT_WEBCONTENT_URL}/v1/extract-webcontent/`, {
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
