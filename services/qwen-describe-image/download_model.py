#!/usr/bin/env python3
"""
Script para descargar el modelo Qwen2-VL-2B-Instruct de forma independiente.
Útil para preparar el modelo antes del deployment o para desarrollo local.
"""

import os
import sys
import logging
from pathlib import Path
from transformers import AutoTokenizer, AutoProcessor, Qwen2_5_VLForConditionalGeneration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_model(model_name: str = "Qwen/Qwen2-VL-2B-Instruct", cache_dir: str = "./models", hf_token: str = None):
    """
    Descarga el modelo Qwen2-VL-2B-Instruct y sus componentes.
    
    Args:
        model_name: Nombre del modelo en Hugging Face
        cache_dir: Directorio donde guardar el modelo
        hf_token: Token de Hugging Face (opcional para modelos públicos)
    """
    
    # Crear directorio de cache
    cache_path = Path(cache_dir).resolve()
    cache_path.mkdir(parents=True, exist_ok=True)
    
    # Configurar autenticación si se proporciona token
    if hf_token:
        os.environ['HF_TOKEN'] = hf_token
        logger.info("Using HF authentication token")
    
    # Configurar variables de entorno
    os.environ['HF_HUB_CACHE'] = str(cache_path)
    os.environ['TRANSFORMERS_CACHE'] = str(cache_path)
    
    logger.info(f"Descargando modelo {model_name} en {cache_path}")
    
    try:
        # Descargar tokenizer
        logger.info("Descargando tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            trust_remote_code=True,
            cache_dir=cache_path
        )
        logger.info("✓ Tokenizer descargado")
        
        # Descargar processor
        logger.info("Descargando processor...")
        processor = AutoProcessor.from_pretrained(
            model_name, 
            trust_remote_code=True,
            cache_dir=cache_path
        )
        logger.info("✓ Processor descargado")
        
        # Descargar modelo completo
        logger.info("Descargando modelo completo (esto puede tomar varios minutos)...")
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=cache_path,
            torch_dtype="auto",  # Usar auto para evitar problemas de memoria durante descarga
            device_map=None      # No mapear a GPU durante descarga
        )
        logger.info("✓ Modelo completo descargado")
        
        # Verificar archivos descargados
        model_cache_name = model_name.replace('/', '--')
        model_path = cache_path / f"models--{model_cache_name}"
        
        if model_path.exists():
            total_size = sum(f.stat().st_size for f in model_path.rglob('*') if f.is_file())
            size_gb = total_size / (1024**3)
            logger.info(f"✓ Modelo descargado exitosamente")
            logger.info(f"  Ubicación: {model_path}")
            logger.info(f"  Tamaño total: {size_gb:.2f} GB")
        else:
            logger.warning("No se encontró el directorio del modelo descargado")
            
    except Exception as e:
        logger.error(f"Error descargando modelo: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Descargar modelo Qwen2-VL-2B-Instruct")
    parser.add_argument(
        "--model", 
        default="Qwen/Qwen2-VL-2B-Instruct",
        help="Nombre del modelo (default: Qwen/Qwen2-VL-2B-Instruct)"
    )
    parser.add_argument(
        "--cache-dir",
        default="./models",
        help="Directorio de cache (default: ./models)"
    )
    parser.add_argument(
        "--hf-token",
        help="Hugging Face token (opcional para modelos públicos)"
    )
    
    args = parser.parse_args()
    
    download_model(args.model, args.cache_dir, args.hf_token)
    logger.info("¡Descarga completada exitosamente!")

if __name__ == "__main__":
    main()
