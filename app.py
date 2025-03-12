import os
from typing import List, Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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
class TokenizeRequest(BaseModel):
    model: str
    text: List[str]

class TokenizeResponse(BaseModel):
    tokens: List[List[str]]

# Create a cache for tokenizers to avoid reloading models
tokenizer_cache = {}

def get_tokenizer(model_name: str):
    """
    Load a tokenizer model, downloading it if necessary and caching it for reuse.
    """
    if model_name in tokenizer_cache:
        logger.info(f"using cached tokenizer for model: {model_name}")
        return tokenizer_cache[model_name]
    
    try:
        logger.info(f"loading tokenizer for model: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            cache_dir=MODELS_DIR,
            local_files_only=False  # This will download if not present
        )
        tokenizer_cache[model_name] = tokenizer
        return tokenizer
    except Exception as e:
        logger.error(f"error loading tokenizer for model {model_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load tokenizer: {str(e)}")

@app.post("/tokenize", response_model=TokenizeResponse)
async def tokenize(request: TokenizeRequest) -> Dict[str, Any]:
    """
    Tokenize the provided text using the specified model.
    """
    logger.info(f"tokenizing {len(request.text)} texts with model: {request.model}")
    
    try:
        tokenizer = get_tokenizer(request.model)
        result = []
        
        for text in request.text:
            # Use the tokenizer to encode the text
            encoded = tokenizer.encode(text, add_special_tokens=False)
            # Convert back to tokens (words)
            tokens = tokenizer.convert_ids_to_tokens(encoded)
            result.append(tokens)
        
        return {"tokens": result}
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