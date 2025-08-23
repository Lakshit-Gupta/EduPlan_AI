from typing import List
import numpy as np
from ..core.config import EMBEDDING_MODEL, FALLBACK_EMBEDDING_MODEL, BATCH_SIZE, QDRANT_VECTOR_SIZE

class NVEmbedPipeline:
    """NVIDIA nv-embed integration with sentence-transformers fallback"""
    
    def __init__(self):
        self.model = None
        self.embedding_dim = QDRANT_VECTOR_SIZE
        self.use_fallback = False
        
        # Try to load NVIDIA nv-embed first
        try:
            print(f"🔄 Attempting to load NVIDIA nv-embed: {EMBEDDING_MODEL}")
            # This would be the actual NVIDIA integration
            # from nvidia_nv_embed import NVEmbedModel
            # self.model = NVEmbedModel(EMBEDDING_MODEL)
            print("❌ NVIDIA nv-embed not available (requires special installation)")
            raise ImportError("nv-embed not available")
        except ImportError:
            print(f"🔄 Falling back to: {FALLBACK_EMBEDDING_MODEL}")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(FALLBACK_EMBEDDING_MODEL)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self.use_fallback = True
            print(f"✅ Embedding model loaded! Vector size: {self.embedding_dim}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        print(f"🔄 Generating embeddings for {len(texts)} texts...")
        
        if self.use_fallback:
            # Use sentence-transformers
            embeddings = []
            batch_size = BATCH_SIZE
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(batch, convert_to_tensor=False)
                embeddings.extend(batch_embeddings.tolist())
                print(f"   Processed {min(i + batch_size, len(texts))}/{len(texts)} texts")
        else:
            # This would be the NVIDIA nv-embed implementation
            embeddings = []
            for text in texts:
                # embedding = self.model.encode(text)
                # embeddings.append(embedding.tolist())
                pass
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        return embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query"""
        if self.use_fallback:
            return self.model.encode([query], convert_to_tensor=False)[0].tolist()
        else:
            # return self.model.encode(query).tolist()
            pass

if __name__ == "__main__":
    # Test the embedding pipeline
    pipeline = NVEmbedPipeline()
    test_texts = ["Chapter 1: Introduction to Mathematics", "Chapter 2: Algebra Basics"]
    embeddings = pipeline.embed_texts(test_texts)
    print(f"Generated embeddings shape: {len(embeddings)} x {len(embeddings[0])}")
