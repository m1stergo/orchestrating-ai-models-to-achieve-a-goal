/**
 * Base product interface with common properties
 */
export interface Product {
  id?: string;
  name: string;
  sku?: string;
  description: string;
  immage_description?: string;
  keywords?: string[];
  category?: string;
  images?: string[];
  audio_description?: string;
  audio?: string;
  audio_config?: Record<string, string>;
  additional_context?: {key: string, value: string }[];
  vendor_url?: string;
  vendor_context?: string;
  selected_context_source?: string;
  uploaded_image?: string;
}

/**
 * Product form data interface for editing (allows undefined values during form editing)
 */
export interface ProductFormData {
  id?: string;
  name?: string;
  sku?: string;
  description?: string;
  keywords?: string[];
  category?: string;
  images?: string[];
  audio_description?: string;
  audio?: string;
  audio_config?: Record<string, string>;
  image_description?: string;
  additional_context?: {key: string, value: string }[];
  vendor_url?: string;
  vendor_context?: string;
  selected_context_source?: string;
  uploaded_image?: string;
}