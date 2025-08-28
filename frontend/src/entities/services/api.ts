const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export async function describeImageWarmup(model: string): Promise<{ status: string, message: string, details?: any }> {
    const response = await fetch(`${API_BASE_URL}/v1/describe-image/warmup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ model })
    })
    if (!response.ok) {
      throw new Error(`Failed to warmup describe image model ${model}: ${response.statusText}`)
    }
    return response.json()
}
  
export async function generateDescriptionWarmup(model: string): Promise<{ status: string, message: string, details?: any }> {
    const response = await fetch(`${API_BASE_URL}/v1/generate-description/warmup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ model })
    })
    if (!response.ok) {
      throw new Error(`Failed to warmup generate description model ${model}: ${response.statusText}`)
    }
    return response.json()
}

export async function describeImageHealthCheck(model: string): Promise<{ status: string, message: string, details?: any }> {
    const response = await fetch(`${API_BASE_URL}/v1/describe-image/healthz`, {
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
    throw new Error(`Failed to describe image health check for ${model}: ${response.statusText}`)
}
  
export async function generateDescriptionHealthCheck(model: string): Promise<{ status: string, message: string, details?: any }> {
  console.log('requestea')
  
  const response = await fetch(`${API_BASE_URL}/v1/generate-description/healthz`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ model })
    })

    console.log('response', response)
    
    // For health checks, we should handle all response codes and return the JSON
    // HTTP 200 = healthy, HTTP 202 = loading, HTTP 503 = unhealthy/error
    if (response.ok || response.status === 202 || response.status === 503) {
      return response.json()
    }
    
    // Only throw for unexpected errors (network issues, 500, etc.)
    throw new Error(`Failed to generate description health check for ${model}: ${response.statusText}`)
}


