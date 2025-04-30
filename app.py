import os
from typing import List, Dict, Any, Optional, Union
import uvicorn
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from transformers import AutoTokenizer
import logging
import hashlib

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
    max_chunk_length: Optional[int] = None  # Maximum character length per chunk
    max_tokens_per_chunk: Optional[int] = None  # Maximum tokens per chunk
    token_overlap: int = 0  # Number of tokens to overlap between chunks

class MultiTextTokenizeRequest(BaseModel):
    model: str
    texts: List[str]
    huggingface_api_key: Optional[str] = None  # Optional Hugging Face API key
    max_chunk_length: Optional[int] = None  # Maximum character length per chunk
    max_tokens_per_chunk: Optional[int] = None  # Maximum tokens per chunk
    token_overlap: int = 0  # Number of tokens to overlap between chunks

class Chunk(BaseModel):
    text: str
    sha256: str
    token_count: int

class TokenizedItem(BaseModel):
    text: str
    sha256: str
    tokens: List[str]
    chunks: List[Chunk]

class SingleTextTokenizeResponse(BaseModel):
    text: str
    sha256: str
    tokens: List[str]
    chunks: List[Chunk]

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
            token = hf_api_key
        else:
            token = None
        
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            cache_dir=MODELS_DIR,
            local_files_only=False,  # This will download if not present
            token=token  # Using 'token' instead of 'use_auth_token'
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

def chunk_text(
    tokenizer, 
    text: str, 
    token_ids: List[int], 
    tokens: List[str],
    max_chunk_length: Optional[int] = None,
    max_tokens_per_chunk: Optional[int] = None,
    token_overlap: int = 0
) -> List[Chunk]:
    """
    Chunk a text based on token and character limits with specified overlap.
    
    Args:
        tokenizer: The tokenizer to use
        text: The original text to chunk
        token_ids: The token IDs from the tokenizer
        tokens: The tokens from the tokenizer
        max_chunk_length: Maximum characters per chunk (if specified)
        max_tokens_per_chunk: Maximum tokens per chunk (if specified)
        token_overlap: Number of tokens to overlap between chunks
    
    Returns:
        List of chunks with their token counts
    """
    # If no chunking parameters are provided, return the entire text as one chunk
    if max_chunk_length is None and max_tokens_per_chunk is None:
        return [Chunk(
            text=text,
            sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),
            token_count=len(tokens)
        )]
    
    # Set default values if only one parameter is provided
    if max_chunk_length is None:
        max_chunk_length = float('inf')  # No character limit
    if max_tokens_per_chunk is None:
        max_tokens_per_chunk = float('inf')  # No token limit
    
    chunks = []
    i = 0
    
    while i < len(tokens):
        # Determine how many tokens to include in this chunk
        chunk_size = min(max_tokens_per_chunk, len(tokens) - i)
        
        # If this is not the first chunk and would be a small final chunk,
        # merge it with the previous chunk if possible
        if i > 0 and chunk_size < max_tokens_per_chunk / 2 and len(chunks) > 0:
            # Get the last chunk's tokens
            previous_chunk = chunks.pop()
            
            # Create a combined chunk
            combined_token_ids = token_ids[i-token_overlap:i+chunk_size] if token_overlap > 0 else token_ids[i:i+chunk_size]
            combined_text = tokenizer.decode(combined_token_ids)
            
            chunks.append(Chunk(
                text=combined_text,
                sha256=hashlib.sha256(combined_text.encode('utf-8')).hexdigest(),
                token_count=len(combined_token_ids)
            ))
            break
        
        # Get the tokens for this chunk
        chunk_tokens = tokens[i:i+chunk_size]
        chunk_token_ids = token_ids[i:i+chunk_size]
        
        # Get the text for this chunk
        chunk_text = tokenizer.decode(chunk_token_ids)
        
        # Create the chunk
        chunks.append(Chunk(
            text=chunk_text,
            sha256=hashlib.sha256(chunk_text.encode('utf-8')).hexdigest(),
            token_count=len(chunk_tokens)
        ))
        
        # If we've covered all tokens, break
        if i + chunk_size >= len(tokens):
            break
            
        # Move to the next chunk, accounting for overlap
        i += max(1, chunk_size - token_overlap)
    
    return chunks

def process_text(
    tokenizer, 
    text: str,
    max_chunk_length: Optional[int] = None,
    max_tokens_per_chunk: Optional[int] = None,
    token_overlap: int = 0
) -> Dict[str, Any]:
    """
    Process a single text: tokenize and chunk it according to specified parameters.
    
    Returns:
        Dictionary with the original text, tokens, and chunks
    """
    # Calculate SHA-256 hash for the text
    text_sha256 = hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    # Tokenize the text
    token_ids = tokenizer.encode(text, add_special_tokens=False)
    tokens = tokenizer.convert_ids_to_tokens(token_ids)
    
    # Create chunks
    chunks = chunk_text(
        tokenizer=tokenizer,
        text=text,
        token_ids=token_ids,
        tokens=tokens,
        max_chunk_length=max_chunk_length,
        max_tokens_per_chunk=max_tokens_per_chunk,
        token_overlap=token_overlap
    )
    
    return {
        "text": text,
        "sha256": text_sha256,
        "tokens": tokens,
        "chunks": chunks
    }

@app.post("/tokenize", response_model=Union[SingleTextTokenizeResponse, MultiTextTokenizeResponse])
async def tokenize(request: Union[SingleTextTokenizeRequest, MultiTextTokenizeRequest]) -> Dict[str, Any]:
    """
    Tokenize and chunk the provided text or texts using the specified model.
    Supports two input formats:
    1. {"model": "modelname", "text": "sentence"} - for single text
    2. {"model": "modelname", "texts": ["sentence1", "sentence2"]} - for multiple texts
    
    Optional parameters:
    - max_chunk_length: Maximum character length per chunk
    - max_tokens_per_chunk: Maximum tokens per chunk
    - token_overlap: Number of tokens to overlap between chunks
    - huggingface_api_key: API key for accessing private or gated models
    """
    try:
        model_name = request.model
        
        # Get the API key from the request body if provided
        api_key = None
        if hasattr(request, 'huggingface_api_key') and request.huggingface_api_key:
            api_key = request.huggingface_api_key
            
        # Get chunking parameters
        max_chunk_length = getattr(request, 'max_chunk_length', None)
        max_tokens_per_chunk = getattr(request, 'max_tokens_per_chunk', None)
        token_overlap = getattr(request, 'token_overlap', 0)
        
        # Get the tokenizer using the API key if provided
        tokenizer = get_tokenizer(model_name, api_key)
        
        # Check if this is a single text request or multiple texts request
        if hasattr(request, 'text'):
            # Single text request
            logger.info(f"processing single text with model: {model_name}")
            return process_text(
                tokenizer=tokenizer,
                text=request.text,
                max_chunk_length=max_chunk_length,
                max_tokens_per_chunk=max_tokens_per_chunk,
                token_overlap=token_overlap
            )
        else:
            # Multiple texts request
            logger.info(f"processing {len(request.texts)} texts with model: {model_name}")
            results = []
            
            for text in request.texts:
                result = process_text(
                    tokenizer=tokenizer,
                    text=text,
                    max_chunk_length=max_chunk_length,
                    max_tokens_per_chunk=max_tokens_per_chunk,
                    token_overlap=token_overlap
                )
                results.append(result)
            
            return {"results": results}
    except Exception as e:
        logger.error(f"error during text processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")

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