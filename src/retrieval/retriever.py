from typing import List, Dict, Any
from ..models.embedding_model import NVEmbedPipeline
from ..database.qdrant_connector import QdrantConnector
from ..core.config import TOP_K_RESULTS

class DocumentRetriever:
    """
    Document retrieval system using embeddings and vector database
    """
    
    def __init__(self):
        """Initialize the retriever with embedding model and database"""
        self.embedding_model = NVEmbedPipeline()
        self.vector_db = QdrantConnector()
        print("🔍 Document retriever initialized")
    
    def retrieve_relevant_documents(
        self, 
        query: str, 
        top_k: int = None,
        filter_chapter: str = None,
        filter_content_type: str = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents relevant to the query
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            filter_chapter: Optional chapter filter
            filter_content_type: Optional content type filter
            
        Returns:
            List of relevant documents with metadata
        """
        if top_k is None:
            top_k = TOP_K_RESULTS
        
        print(f"🔍 Searching for: '{query}'")
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.embed_query(query)
            
            # Search in vector database
            results = self.vector_db.search_documents(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_chapter=filter_chapter,
                filter_content_type=filter_content_type
            )
            
            print(f"📊 Found {len(results)} relevant documents")
            
            # Log top results
            for i, result in enumerate(results[:3], 1):
                print(f"   {i}. Score: {result['score']:.4f} | Chapter: {result['chapter']} | Type: {result['content_type']}")
                print(f"      Text preview: {result['text'][:100]}...")
            
            return results
            
        except Exception as e:
            print(f"❌ Error retrieving documents: {str(e)}")
            return []
    
    def retrieve_by_chapter(self, chapter: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve all documents from a specific chapter
        
        Args:
            chapter: Chapter name/number
            top_k: Maximum number of documents to retrieve
            
        Returns:
            List of documents from the chapter
        """
        if top_k is None:
            top_k = TOP_K_RESULTS * 2  # Get more for chapter-specific retrieval
        
        print(f"📚 Retrieving documents from: {chapter}")
        
        try:
            # Use a generic query with chapter filter
            generic_query = "educational content and learning material"
            query_embedding = self.embedding_model.embed_query(generic_query)
            
            # Search with chapter filter
            results = self.vector_db.search_documents(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_chapter=chapter
            )
            
            print(f"📊 Found {len(results)} documents in chapter {chapter}")
            return results
            
        except Exception as e:
            print(f"❌ Error retrieving chapter documents: {str(e)}")
            return []
    
    def retrieve_context_for_generation(
        self, 
        topic: str, 
        subject: str = None,
        chapter: str = None,
        top_k: int = 5
    ) -> str:
        """
        Retrieve and format context for lesson plan generation
        
        Args:
            topic: Main topic for the lesson plan
            subject: Optional subject filter
            chapter: Optional chapter filter
            top_k: Number of documents to retrieve
            
        Returns:
            Formatted context string
        """
        print(f"📖 Retrieving context for topic: '{topic}'")
        
        # Create enhanced query
        enhanced_query = f"{topic} educational content lesson material"
        if subject:
            enhanced_query += f" {subject}"
        
        # Retrieve relevant documents
        documents = self.retrieve_relevant_documents(
            query=enhanced_query,
            top_k=top_k,
            filter_chapter=chapter
        )
        
        if not documents:
            print("⚠️ No relevant documents found")
            return "No relevant educational content found for this topic."
        
        # Format context
        context_parts = []
        context_parts.append(f"EDUCATIONAL CONTEXT FOR: {topic.upper()}")
        context_parts.append("=" * 50)
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"\n[REFERENCE {i}] Chapter {doc['chapter']} - {doc['content_type'].title()}")
            context_parts.append(f"Relevance Score: {doc['score']:.4f}")
            context_parts.append(f"Content: {doc['text']}")
            context_parts.append("-" * 40)
        
        context = "\n".join(context_parts)
        
        print(f"✅ Generated context from {len(documents)} sources ({len(context)} characters)")
        return context
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        try:
            return self.vector_db.get_collection_info()
        except Exception as e:
            print(f"❌ Error getting database stats: {str(e)}")
            return {}

if __name__ == "__main__":
    # Test the retriever
    retriever = DocumentRetriever()
    
    # Test search
    results = retriever.retrieve_relevant_documents("evaporation and water cycle", top_k=3)
    print(f"\nTest search returned {len(results)} results")
    
    # Test context generation
    context = retriever.retrieve_context_for_generation("evaporation", top_k=2)
    print(f"\nGenerated context length: {len(context)} characters")