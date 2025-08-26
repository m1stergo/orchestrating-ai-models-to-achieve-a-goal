import type { CreateProductFormData, UpdateProductFormData } from './schema'
import type { Product } from './types'

const API_URL = `${import.meta.env.VITE_API_BASE_URL}/v1/products`

/**
 * Fetch all products from the API
 * @returns Promise with array of products
 */
export async function getAllProducts(): Promise<Product[]> {
  const response = await fetch(`${API_URL}/`)
  if (!response.ok) {
    throw new Error(`Failed to fetch products: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch a single product by ID
 * @param id - Product ID
 * @returns Promise with the product
 */
export async function getProductById(id: number): Promise<Product> {
  const response = await fetch(`${API_URL}/${id}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch product ${id}: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Create a new product
 * @param product - Product data
 * @returns Promise with the created product
 */
export async function createProduct(product: CreateProductFormData): Promise<Product> {
  const response = await fetch(`${API_URL}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(product),
  })
  if (!response.ok) {
    throw new Error(`Failed to create product: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Update an existing product
 * @param product - Updated product data
 * @returns Promise with the updated product
 */
export async function updateProduct(product: UpdateProductFormData): Promise<Product> {
  const response = await fetch(`${API_URL}/${product.id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(product),
  })
  if (!response.ok) {
    throw new Error(`Failed to update product ${product.id}: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Delete a product
 * @param id - Product ID
 * @returns Promise with the deleted product
 */
export async function deleteProduct(id: number): Promise<Product> {
  const response = await fetch(`${API_URL}/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(`Failed to delete product ${id}: ${response.statusText}`)
  }
  return response.json()
}
