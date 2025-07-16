import numpy as np
import faiss
from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Dict, Any
import pickle
import os
from config import Config
from retrieval import Source

class EmbeddingManager:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        self.index = None
        self.source_metadata = []
        
    def encode_text(self, texts: List[str]) -> np.ndarray:
        encoded = self.tokenizer(
            texts, 
            padding=True, 
            truncation=True, 
            max_length=512, 
            return_tensors='pt'
        )
        
        with torch.no_grad():
            encoded = {k: v.to(self.device) for k, v in encoded.items()}
            outputs = self.model(**encoded)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            
        return embeddings.cpu().numpy()
    
    def create_index(self, sources: List[Source]) -> None:
        texts = [f"{source.title} {source.content}" for source in sources]
        embeddings = self.encode_text(texts)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype(np.float32))
        
        self.source_metadata = sources
    
    def search_similar(self, query: str, top_k: int = None) -> List[Source]:
        if self.index is None:
            return []
        
        top_k = top_k or Config.RETRIEVAL_TOP_K
        
        query_embedding = self.encode_text([query])
        faiss.normalize_L2(query_embedding)
        
        scores, indices = self.index.search(query_embedding.astype(np.float32), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.source_metadata):
                source = self.source_metadata[idx]
                source.relevance_score = float(score)
                results.append(source)
        
        return results
    
    def save_index(self, path: str = None) -> None:
        path = path or Config.FAISS_INDEX_PATH
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        if self.index is not None:
            faiss.write_index(self.index, f"{path}.index")
            
            with open(f"{path}_metadata.pkl", 'wb') as f:
                pickle.dump(self.source_metadata, f)
    
    def load_index(self, path: str = None) -> None:
        path = path or Config.FAISS_INDEX_PATH
        
        try:
            self.index = faiss.read_index(f"{path}.index")
            
            with open(f"{path}_metadata.pkl", 'rb') as f:
                self.source_metadata = pickle.load(f)
        except FileNotFoundError:
            print("No existing index found. Please create one first.")
            self.index = None
            self.source_metadata = []