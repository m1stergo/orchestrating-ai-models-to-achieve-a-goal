/**
 * Base product interface with common properties
 */
export interface ProductBase {
  name: string;
  sku?: string;
  description: string;
  keywords?: string[];
  category?: string;
  images?: string[];
  audio_description?: string;
  audio?: string;
}

/**
 * Product creation interface - used when creating new products
 */
export interface ProductCreate extends ProductBase {}

/**
 * Product update interface - used when updating existing products
 */
export interface ProductUpdate extends ProductBase {
  id: number;
}

/**
 * Complete product interface with all properties
 */
export interface Product extends ProductBase {
  id: number;
}

/**
 * Type guard to check if an object is a Product
 */
export function isProduct(obj: any): obj is Product {
  return obj && typeof obj === 'object' && 
    typeof obj.id === 'number' && 
    typeof obj.name === 'string';
}
