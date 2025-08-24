import torch
from transformers import AutoModel, AutoTokenizer
import numpy as np
from typing import List, Union

class NVEmbed:
    """Class for generating embeddings with NVIDIA NV-Embed models"""
    
    def __init__(self, model_name="nvidia/NV-Embed-v2"):
        """
        Initialize the NVEmbed model
        
        Args:
            model_name: Name of the model to load
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        
        print(f"✅ Loaded {model_name} on {self.device}")
    
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Either a single text string or a list of text strings
            
        Returns:
            np.ndarray: Array of embeddings
        """
        # Handle single text input
        if isinstance(texts, str):
            texts = [texts]
            
        # Tokenize texts
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Use mean pooling
        attention_mask = inputs["attention_mask"]
        last_hidden_state = outputs.last_hidden_state
        
        # Apply attention mask for mean pooling
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
        sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)  # Prevent division by zero
        embeddings = sum_embeddings / sum_mask
        
        # Return as numpy array
        return embeddings.cpu().numpy()
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        return self.model.config.hidden_size
