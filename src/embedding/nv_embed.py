from typing import List, Union
import sys
import os
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NVEmbeddings:
    """
    Class for encoding text using NVIDIA nv-embed models
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the nv-embed model
        """
        self.model_name = model_name or config.EMBEDDING_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        batch_size = config.BATCH_SIZE
        
        # Process in batches to avoid memory issues
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Tokenize and get embeddings
            inputs = self.tokenizer(
                batch, 
                padding=True, 
                truncation=True, 
                return_tensors="pt",
                max_length=512
            ).to(self.device)
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling to get document embeddings
                attention_mask = inputs["attention_mask"]
                token_embeddings = outputs.last_hidden_state
                
                # Mean pooling
                input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                batch_embeddings = (sum_embeddings / sum_mask).cpu().numpy()
                
                # Normalize embeddings
                batch_embeddings = batch_embeddings / np.linalg.norm(batch_embeddings, axis=1, keepdims=True)
                
                embeddings.extend(batch_embeddings.tolist())
        
        return embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query text
        
        Args:
            query: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.embed_texts([query])[0]
