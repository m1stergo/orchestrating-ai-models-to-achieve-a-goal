/**
 * Base product interface with common properties
 */
export interface Product {
  id?: string;
  name: string;
  sku?: string;
  description: string;
  keywords?: string[];
  category?: string;
  images?: string[];
  audio_description?: string;
  audio?: string;
  audio_config?: Record<string, string>;
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
}