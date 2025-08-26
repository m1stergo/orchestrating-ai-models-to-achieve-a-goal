import { z } from 'zod'

export const ProductSchema = z.object({
  id: z.any().optional(),
  name: z.string().nonempty('Product name is required'),
  sku: z.string().nonempty('SKU is required'),
  description: z.string().nonempty('Description is required'),
  keywords: z.array(z.string()).optional(),
  category: z.string().optional(),
  images: z.array(z.string()).optional(),
  audio_description: z.string().optional(),
  audio: z.string().optional(),
})

export type ProductFormData = z.infer<typeof ProductSchema>

// Schema for creation (without id)
export const CreateProductSchema = ProductSchema.omit({ id: true })
export type CreateProductFormData = z.infer<typeof CreateProductSchema>

// Schema for updates (id required)
export const UpdateProductSchema = ProductSchema.extend({
  id: z.any()
})
export type UpdateProductFormData = z.infer<typeof UpdateProductSchema>
