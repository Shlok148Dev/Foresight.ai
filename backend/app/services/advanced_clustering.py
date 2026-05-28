import hdbscan
import faiss
import numpy as np
from typing import List, Dict

class AdvancedClusteringEngine:
    """Advanced clustering using HDBSCAN + FAISS"""
    
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=2)
        self.faiss_index = faiss.IndexFlatL2(embedding_dim)
    
    def cluster_signals(self, signals: List[Dict]) -> Dict:
        """Cluster signals using HDBSCAN"""
        if not signals:
            return {
                "clusters": {},
                "cluster_labels": [],
                "noise_points": [],
                "cluster_quality": 0.0,
                "num_clusters": 0
            }

        embeddings = np.array([s["embedding"] for s in signals])
        
        # If there are fewer than min_cluster_size signals, hdbscan will fail or mark all as noise.
        # Fall back gracefully.
        if len(signals) < 5:
            return {
                "clusters": {-1: signals},
                "cluster_labels": [-1]*len(signals),
                "noise_points": signals,
                "cluster_quality": 0.0,
                "num_clusters": 0
            }

        labels = self.clusterer.fit_predict(embeddings)
        
        self.faiss_index.add(embeddings.astype(np.float32))
        
        clusters = {}
        noise_points = []
        
        for idx, label in enumerate(labels):
            if label == -1:
                noise_points.append(signals[idx])
            else:
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(signals[idx])
        
        cluster_quality = self._calculate_cluster_quality(embeddings, labels)
        
        return {
            "clusters": clusters,
            "cluster_labels": labels.tolist(),
            "noise_points": noise_points,
            "cluster_quality": cluster_quality,
            "num_clusters": len(clusters)
        }
    
    def find_similar_signals(self, query_embedding: np.ndarray, k: int = 10) -> List[int]:
        """Find similar signals using FAISS"""
        if self.faiss_index.ntotal == 0:
            return []
        
        k = min(k, self.faiss_index.ntotal)
        distances, indices = self.faiss_index.search(
            query_embedding.reshape(1, -1).astype(np.float32),
            k
        )
        return indices[0].tolist()
    
    def _calculate_cluster_quality(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """Calculate clustering quality"""
        from sklearn.metrics import silhouette_score
        
        if len(np.unique(labels)) < 2:
            return 0.0
        
        mask = labels != -1
        if np.sum(mask) < 2:
            return 0.0
        
        try:
            score = silhouette_score(embeddings[mask], labels[mask])
            return float((score + 1) / 2)
        except Exception:
            return 0.0
