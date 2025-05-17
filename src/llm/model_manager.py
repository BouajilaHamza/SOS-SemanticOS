"""
Model Manager component for Local LLM Integration.

This component handles loading and initialization of the language model.
It manages model resources efficiently and supports model switching.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import threading
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


class ModelManager:
    """
    Handles loading and initialization of the language model.
    
    This class is responsible for:
    1. Managing model resources efficiently
    2. Supporting model switching and version management
    3. Implementing quantization and optimization techniques for performance
    """
    
    def __init__(self, model_dir: str, model_name: str = "microsoft/phi-2", device: str = None):
        """
        Initialize the ModelManager.
        
        Args:
            model_dir: Directory to store downloaded models
            model_name: Name or path of the model to load (default: microsoft/phi-2)
            device: Device to run the model on (default: auto-detect)
        """
        self.model_dir = Path(model_dir).expanduser().absolute()
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        # Initialize model and tokenizer to None
        self.model = None
        self.tokenizer = None
        self.lock = threading.RLock()
        
        # Model metadata
        self.model_metadata = {
            "name": model_name,
            "loaded": False,
            "quantized": False,
            "device": self.device,
            "max_length": 2048,  # Default, will be updated after loading
        }
    
    def load_model(self, quantize: bool = True) -> bool:
        """
        Load the model and tokenizer.
        
        Args:
            quantize: Whether to apply quantization for reduced memory usage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                print(f"Loading model {self.model_name}...")
                
                # Configure quantization if requested
                quantization_config = None
                if quantize and self.device == "cuda":
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_use_double_quant=True
                    )
                    self.model_metadata["quantized"] = True
                
                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    cache_dir=str(self.model_dir),
                    trust_remote_code=True
                )
                
                # Load model
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    cache_dir=str(self.model_dir),
                    quantization_config=quantization_config,
                    device_map=self.device,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
                
                # Update metadata
                self.model_metadata["loaded"] = True
                if hasattr(self.model.config, "max_position_embeddings"):
                    self.model_metadata["max_length"] = self.model.config.max_position_embeddings
                
                print(f"Model loaded successfully on {self.device}")
                return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def unload_model(self) -> bool:
        """
        Unload the model to free up memory.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                if self.model is not None:
                    # Delete model and tokenizer
                    del self.model
                    del self.tokenizer
                    
                    # Force garbage collection
                    import gc
                    gc.collect()
                    
                    # Clear CUDA cache if available
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    
                    # Reset model and tokenizer to None
                    self.model = None
                    self.tokenizer = None
                    
                    # Update metadata
                    self.model_metadata["loaded"] = False
                    
                    print("Model unloaded successfully")
                    return True
                return True  # Already unloaded
        except Exception as e:
            print(f"Error unloading model: {e}")
            return False
    
    def switch_model(self, model_name: str, quantize: bool = True) -> bool:
        """
        Switch to a different model.
        
        Args:
            model_name: Name or path of the new model
            quantize: Whether to apply quantization for reduced memory usage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Unload current model
            self.unload_model()
            
            # Update model name
            self.model_name = model_name
            self.model_metadata["name"] = model_name
            
            # Load new model
            return self.load_model(quantize=quantize)
        except Exception as e:
            print(f"Error switching model: {e}")
            return False
    
    def is_model_loaded(self) -> bool:
        """
        Check if the model is loaded.
        
        Returns:
            True if the model is loaded, False otherwise
        """
        return self.model is not None and self.tokenizer is not None
    
    def get_model_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the current model.
        
        Returns:
            Dictionary of model metadata
        """
        return self.model_metadata.copy()
    
    def get_model_and_tokenizer(self) -> tuple:
        """
        Get the model and tokenizer objects.
        
        Returns:
            Tuple of (model, tokenizer)
        """
        return self.model, self.tokenizer
