import os
from typing import List, Dict, Any, Optional, Union
import uvicorn
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from transformers import AutoTokenizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the models directory for caching
MODELS_DIR = "./models"

# Ensure models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(title="Model Tokenizer Microservice")

# Define request and response models
class SingleTextTokenizeRequest(BaseModel):
    model: str
    text: str
    huggingface_api_key: Optional[str] = None  # Optional Hugging Face API key

class MultiTextTokenizeRequest(BaseModel):
    model: str
    texts: List[str]
    huggingface_api_key: Optional[str] = None  # Optional Hugging Face API key

class TokenizedItem(BaseModel):
    text: str
    tokens: List[str]

class SingleTextTokenizeResponse(BaseModel):
    text: str
    tokens: List[str]

class MultiTextTokenizeResponse(BaseModel):
    results: List[TokenizedItem]

# Create a cache for tokenizers to avoid reloading models
tokenizer_cache = {}

def get_tokenizer(model_name: str, hf_api_key: Optional[str] = None):
    """
    Load a tokenizer model, downloading it if necessary and caching it for reuse.
    
    Args:
        model_name: The name of the Hugging Face model to load
        hf_api_key: Optional Hugging Face API key for accessing private or gated models
    """
    # Create a cache key that includes the API key (if provided)
    # This ensures we don't reuse a tokenizer loaded with a different API key
    cache_key = f"{model_name}_{hf_api_key if hf_api_key else 'public'}"
    
    if cache_key in tokenizer_cache:
        logger.info(f"using cached tokenizer for model: {model_name}")
        return tokenizer_cache[cache_key]
    
    try:
        logger.info(f"loading tokenizer for model: {model_name}")
        
        # Set the Hugging Face token if provided
        if hf_api_key:
            logger.info(f"using provided Hugging Face API key for model: {model_name}")
            os.environ["HF_TOKEN"] = hf_api_key
            use_auth_token = True
        else:
            use_auth_token = False
        
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            cache_dir=MODELS_DIR,
            local_files_only=False,  # This will download if not present
            use_auth_token=use_auth_token  # Use the API key if provided
        )
        
        tokenizer_cache[cache_key] = tokenizer
        return tokenizer
    except Exception as e:
        logger.error(f"error loading tokenizer for model {model_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load tokenizer: {str(e)}")

def tokenize_text(tokenizer, text: str) -> List[str]:
    """
    Tokenize a single text string and return the list of tokens.
    """
    encoded = tokenizer.encode(text, add_special_tokens=False)
    return tokenizer.convert_ids_to_tokens(encoded)

@app.post("/tokenize", response_model=Union[SingleTextTokenizeResponse, MultiTextTokenizeResponse])
async def tokenize(request: Union[SingleTextTokenizeRequest, MultiTextTokenizeRequest]) -> Dict[str, Any]:
    """
    Tokenize the provided text or texts using the specified model.
    Supports two input formats:
    1. {"model": "modelname", "text": "sentence"} - for single text
    2. {"model": "modelname", "texts": ["sentence1", "sentence2"]} - for multiple texts
    
    A Hugging Face API key can be provided in the request body as huggingface_api_key
    for accessing private or gated models.
    """
    try:
        model_name = request.model
        
        # Get the API key from the request body if provided
        api_key = None
        if hasattr(request, 'huggingface_api_key') and request.huggingface_api_key:
            api_key = request.huggingface_api_key
            
        # Get the tokenizer using the API key if provided
        tokenizer = get_tokenizer(model_name, api_key)
        
        # Check if this is a single text request or multiple texts request
        if hasattr(request, 'text'):
            # Single text request
            logger.info(f"tokenizing single text with model: {model_name}")
            tokens = tokenize_text(tokenizer, request.text)
            return {"text": request.text, "tokens": tokens}
        else:
            # Multiple texts request
            logger.info(f"tokenizing {len(request.texts)} texts with model: {model_name}")
            results = []
            
            for text in request.texts:
                tokens = tokenize_text(tokenizer, text)
                results.append({"text": text, "tokens": tokens})
            
            return {"results": results}
    except Exception as e:
        logger.error(f"error during tokenization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tokenization failed: {str(e)}")

@app.head("/")
@app.get("/")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy"}

def main():
    """
    Run the FastAPI application with uvicorn.
    """
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()