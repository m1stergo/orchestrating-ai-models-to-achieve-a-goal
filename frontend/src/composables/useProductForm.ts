import { inject } from 'vue'
import type { useForm } from 'vee-validate'
import type { ProductFormData } from '@/entities/products'

/**
 * Composable para acceder al formulario de producto inyectado
 * Proporciona tipado completo para useForm<ProductFormData>
 */
export function useProductForm() {
  const form = inject<ReturnType<typeof useForm<ProductFormData>>>('form')!
  
  return form
}
