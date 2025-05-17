"""
Inference Engine component for Local LLM Integration.

This component executes model inference and processes the results.
It handles batching, queuing, and implements fallback strategies.
"""

import time
import threading
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
import torch
from transformers import StoppingCriteria, StoppingCriteriaList


class StopOnTokens(StoppingCriteria):
    """Custom stopping criteria for text generation."""
    
    def __init__(self, stop_token_ids: List[int]):
        """
        Initialize with stop token IDs.
        
        Args:
            stop_token_ids: List of token IDs that should trigger stopping
        """
        self.stop_token_ids = stop_token_ids
        
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        """
        Check if generation should stop.
        
        Args:
            input_ids: Current sequence of token IDs
            scores: Model scores for next tokens
            
        Returns:
            True if generation should stop, False otherwise
        """
        for stop_id in self.stop_token_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False


class InferenceEngine:
    """
    Executes model inference and processes the results.
    
    This class is responsible for:
    1. Handling batching and queuing of inference requests
    2. Implementing fallback strategies for handling model limitations
    3. Providing mechanisms for response validation and filtering
    """
    
    def __init__(self, model_manager):
        """
        Initialize the InferenceEngine.
        
        Args:
            model_manager: Reference to the ModelManager instance
        """
        self.model_manager = model_manager
        self.lock = threading.RLock()
        self.inference_queue = []
        self.is_processing = False
        self.default_generation_params = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "do_sample": True
        }
    
    def generate_text(self, 
                     prompt: str, 
                     generation_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate text based on the given prompt.
        
        Args:
            prompt: Input prompt for text generation
            generation_params: Parameters for text generation
            
        Returns:
            Generated text
        """
        try:
            with self.lock:
                # Ensure model is loaded
                if not self.model_manager.is_model_loaded():
                    success = self.model_manager.load_model()
                    if not success:
                        return "Error: Failed to load language model."
                
                # Get model and tokenizer
                model, tokenizer = self.model_manager.get_model_and_tokenizer()
                
                # Merge default and custom generation parameters
                params = self.default_generation_params.copy()
                if generation_params:
                    params.update(generation_params)
                
                # Tokenize input
                inputs = tokenizer(prompt, return_tensors="pt")
                input_ids = inputs["input_ids"].to(self.model_manager.device)
                
                # Set up stopping criteria
                stop_token_ids = []
                
                # Add model-specific stop tokens
                model_name = self.model_manager.model_name.lower()
                if "phi" in model_name:
                    # Phi models use specific tokens for end of assistant response
                    stop_tokens = ["<|end|>"]
                    for token in stop_tokens:
                        stop_ids = tokenizer.encode(token, add_special_tokens=False)
                        stop_token_ids.extend(stop_ids)
                elif "llama" in model_name:
                    # LLaMA models use specific tokens for end of response
                    stop_tokens = ["[INST]", "</s>"]
                    for token in stop_tokens:
                        stop_ids = tokenizer.encode(token, add_special_tokens=False)
                        stop_token_ids.extend(stop_ids)
                
                # Add common stop tokens
                stop_token_ids.append(tokenizer.eos_token_id)
                
                # Create stopping criteria
                stopping_criteria = StoppingCriteriaList([StopOnTokens(stop_token_ids)])
                
                # Generate text
                with torch.no_grad():
                    output = model.generate(
                        input_ids,
                        stopping_criteria=stopping_criteria,
                        pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
                        **params
                    )
                
                # Decode output
                generated_text = tokenizer.decode(output[0][input_ids.shape[1]:], skip_special_tokens=True)
                
                # Clean up model-specific formatting
                if "phi" in model_name:
                    # Remove any trailing <|end|> tokens
                    generated_text = generated_text.replace("<|end|>", "").strip()
                elif "llama" in model_name:
                    # Remove any trailing [INST] or </s> tokens
                    generated_text = generated_text.split("[INST]")[0].strip()
                    generated_text = generated_text.split("</s>")[0].strip()
                
                return generated_text
        except Exception as e:
            print(f"Error generating text: {e}")
            return f"Error during text generation: {str(e)}"
    
    def generate_with_fallback(self, 
                              prompt: str, 
                              generation_params: Optional[Dict[str, Any]] = None,
                              max_retries: int = 2) -> str:
        """
        Generate text with fallback strategies for handling errors.
        
        Args:
            prompt: Input prompt for text generation
            generation_params: Parameters for text generation
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated text
        """
        retries = 0
        while retries <= max_retries:
            try:
                # Attempt generation with current parameters
                result = self.generate_text(prompt, generation_params)
                
                # Check if result indicates an error
                if result.startswith("Error:"):
                    # Modify parameters for retry
                    if generation_params is None:
                        generation_params = self.default_generation_params.copy()
                    
                    # Reduce complexity for retry
                    if "temperature" in generation_params:
                        generation_params["temperature"] = max(0.2, generation_params["temperature"] - 0.2)
                    if "max_new_tokens" in generation_params:
                        generation_params["max_new_tokens"] = max(128, generation_params["max_new_tokens"] // 2)
                    
                    retries += 1
                    continue
                
                return result
            except Exception as e:
                print(f"Error in generation attempt {retries + 1}: {e}")
                retries += 1
                
                # Wait before retry
                time.sleep(1)
        
        # If all retries fail, return a fallback message
        return "I apologize, but I'm having trouble generating a response at the moment. Please try again with a simpler query."
    
    def validate_response(self, response: str, criteria: Dict[str, Any]) -> bool:
        """
        Validate a generated response against specified criteria.
        
        Args:
            response: Generated response text
            criteria: Validation criteria
            
        Returns:
            True if response meets criteria, False otherwise
        """
        # Check minimum length
        if "min_length" in criteria and len(response) < criteria["min_length"]:
            return False
        
        # Check maximum length
        if "max_length" in criteria and len(response) > criteria["max_length"]:
            return False
        
        # Check for required content
        if "required_content" in criteria:
            for required in criteria["required_content"]:
                if required not in response:
                    return False
        
        # Check for prohibited content
        if "prohibited_content" in criteria:
            for prohibited in criteria["prohibited_content"]:
                if prohibited in response:
                    return False
        
        return True
    
    def generate_until_valid(self, 
                           prompt: str, 
                           validation_criteria: Dict[str, Any],
                           generation_params: Optional[Dict[str, Any]] = None,
                           max_attempts: int = 3) -> str:
        """
        Generate text until it meets validation criteria.
        
        Args:
            prompt: Input prompt for text generation
            validation_criteria: Criteria for validating responses
            generation_params: Parameters for text generation
            max_attempts: Maximum number of generation attempts
            
        Returns:
            Valid generated text or error message
        """
        for attempt in range(max_attempts):
            response = self.generate_text(prompt, generation_params)
            
            if self.validate_response(response, validation_criteria):
                return response
            
            # Modify parameters for next attempt
            if generation_params is None:
                generation_params = self.default_generation_params.copy()
            
            # Adjust parameters based on validation failures
            if "min_length" in validation_criteria and len(response) < validation_criteria["min_length"]:
                # Increase max_new_tokens for longer responses
                generation_params["max_new_tokens"] = int(generation_params.get("max_new_tokens", 512) * 1.5)
            
            if "max_length" in validation_criteria and len(response) > validation_criteria["max_length"]:
                # Decrease max_new_tokens for shorter responses
                generation_params["max_new_tokens"] = int(generation_params.get("max_new_tokens", 512) * 0.7)
        
        # If all attempts fail, return the last response with a warning
        return f"Note: This response may not meet all requirements.\n\n{response}"
