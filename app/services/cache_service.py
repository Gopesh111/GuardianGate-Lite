import faiss
import numpy as np
import json
import os
import yaml
from fastembed import TextEmbedding

# Load Policy Config for FinOps Guardrails
with open("config.yaml", "r") as file:
    POLICY = yaml.safe_load(file)

METRICS_FILE = "metrics.json"

class SemanticCache:
    def __init__(self, threshold=0.85):
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.dimension = 384
        self.threshold = threshold
        
        # Load previous cache hits AND api calls from hard drive
        self.cache_hits, self.api_calls = self._load_metrics()
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self.cache_payloads = [] 

    def _load_metrics(self):
        """Loads previous metrics from JSON file if it exists."""
        if os.path.exists(METRICS_FILE):
            try:
                with open(METRICS_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("cache_hits", 0), data.get("api_calls", 0)
            except Exception:
                pass
        return 0, 0

    def _save_metrics(self):
        """Saves current metrics to JSON file."""
        with open(METRICS_FILE, "w") as f:
            json.dump({"cache_hits": self.cache_hits, "api_calls": self.api_calls}, f)

    def enforce_budget(self) -> bool:
        """FinOps Guardrail: Prevent API calls if budget exceeded"""
        current_cost = self.api_calls * POLICY['budget']['cost_per_call']
        if current_cost >= POLICY['budget']['daily_limit_usd']:
            return False # Budget exhausted!
        return True

    def get_embedding(self, text: str) -> np.ndarray:
        embeddings = list(self.embedding_model.embed([text]))
        vector = embeddings[0]
        faiss.normalize_L2(vector.reshape(1, -1))
        return vector.reshape(1, -1)

    def check_cache(self, prompt: str, dynamic_threshold: float = None):
        current_threshold = dynamic_threshold if dynamic_threshold is not None else self.threshold

        if self.index.ntotal == 0:
            return None, 0.0 
            
        vector = self.get_embedding(prompt)
        distances, indices = self.index.search(vector, k=1)
        
        similarity_score = distances[0][0]
        match_index = indices[0][0]
        
        if similarity_score >= current_threshold:
            # Semantic Hit!
            self.cache_hits += 1
            self._save_metrics() 
            return self.cache_payloads[match_index], float(similarity_score)
            
        return None, float(similarity_score)

    def add_to_cache(self, prompt: str, response: str):
        vector = self.get_embedding(prompt)
        self.index.add(vector)
        self.cache_payloads.append(response)
        
        # THE FIX: Increment API Calls on Cache Miss!
        self.api_calls += 1 
        self._save_metrics()

# Create a global singleton instance
semantic_cache = SemanticCache(threshold=0.85)