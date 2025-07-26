/**
 * Base product interface with common properties
 */
export interface ProductBase {
  name: string;
  description?: string;
  images?: string[];
  audio?: string;
}

/**
 * Interface for creating a new product
 */
export interface ProductCreate extends ProductBase {}

/**
 * Interface for updating an existing product
 * All fields are optional for partial updates
 */
export interface ProductUpdate {
  id: number;
  name?: string;
  description?: string;
  images?: string[];
  audio?: string;
}

/**
 * Complete product interface with all properties
 * This is what we receive from the API
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
