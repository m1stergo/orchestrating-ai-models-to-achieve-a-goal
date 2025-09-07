const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

type DescribeImageWarmupParams = {
    model: string
}
export async function describeImageWarmup(params: DescribeImageWarmupParams): Promise<{ id: string, status: string, details?: any }> {
    const response = await fetch(`${API_BASE_URL}/v1/describe-image/warmup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params)
    })
    if (!response.ok) {
      throw new Error(`Failed to warmup describe image model ${params.model}: ${response.statusText}`)
    }
    return response.json()
}

type DescribeImageStatusParams = {
    model: string,
    job_id: string
}
export async function describeImageStatus(params: DescribeImageStatusParams): Promise<{ id: string, status: string, details?: any }> {
  const response = await fetch(`${API_BASE_URL}/v1/describe-image/status`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params)
  })
  if (!response.ok) {
    throw new Error(`Failed to get status of describe image model ${params.model}: ${response.statusText}`)
  }
  return response.json()
}
  
type DescribeImageInferenceParams = {
    model: string,
    image_url: string,
    prompt?: string
}
export async function describeImageInference(params: DescribeImageInferenceParams): Promise<{ id: string, status: string, details?: any }> {
    const response = await fetch(`${API_BASE_URL}/v1/describe-image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params)
    })
    if (!response.ok) {
      throw new Error(`Failed to describe image model ${params.model}: ${response.statusText}`)
    }
    return response.json()
}
  
export async function generateDescriptionHealthCheck(model: string): Promise<{ status: string, details?: any }> {
  const response = await fetch(`${API_BASE_URL}/v1/generate-description/healthz`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ model })
    })

    // For health checks, we should handle all response codes and return the JSON
    // HTTP 200 = healthy, HTTP 202 = loading, HTTP 503 = unhealthy/error
    if (response.ok || response.status === 202 || response.status === 503) {
      return response.json()
    }
    
    // Only throw for unexpected errors (network issues, 500, etc.)
    throw new Error(`Failed to generate description health check for ${model}: ${response.statusText}`)
}


