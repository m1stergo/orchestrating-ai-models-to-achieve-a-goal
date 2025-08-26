// Export API functions
export { getAllProducts, getProductById, createProduct, updateProduct, deleteProduct } from './api'

// Export types
export type { Product, ProductFormData } from './types'

// Export Zod schemas and types
export { ProductSchema, CreateProductSchema, UpdateProductSchema } from './schema'
export type { CreateProductFormData, UpdateProductFormData } from './schema'
