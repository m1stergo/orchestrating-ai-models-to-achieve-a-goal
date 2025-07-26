/**
 * Types for web content extraction
 */

/**
 * Schema for web content extraction request.
 */
export interface ExtractSiteContentRequest {
  url: string
}

/**
 * Schema for web content extraction response.
 */
export interface ExtractSiteContentResponse {
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
