import type { ExtractSiteContentRequest, ExtractSiteContentResponse, UploadImageResponse, DescribeImageResponse } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const DESCRIBE_IMAGE_URL = `${API_BASE_URL}/api/v1/describe-image`
const EXTRACT_SITE_CONTENT_URL = `${API_BASE_URL}/api/v1/extract-site-content/`
const UPLOAD_IMAGE_URL = `${API_BASE_URL}/api/v1/upload-image/` 

export async function uploadImage(formData: FormData): Promise<UploadImageResponse> {
  const response = await fetch(UPLOAD_IMAGE_URL, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) {
    throw new Error(`Failed to upload image: ${response.statusText}`)
  }
  return response.json()
}

export async function describeImage(image: string): Promise<DescribeImageResponse> {
  const response = await fetch(DESCRIBE_IMAGE_URL, {
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

export async function extractSiteContent(url: string): Promise<ExtractSiteContentResponse> {
  let formattedUrl = url;
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    formattedUrl = `https://${url}`;
  }
  
  const request: ExtractSiteContentRequest = { url: formattedUrl }
  
  const response = await fetch(EXTRACT_SITE_CONTENT_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  
  if (!response.ok) {
    throw new Error(`Failed to extract content: ${response.statusText}`)
  }

  return response.json() as Promise<ExtractSiteContentResponse>
}
