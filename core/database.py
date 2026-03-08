from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

class VectorDB:
    def __init__(self):
        # Local storage mode; creates a folder named 'cinesearch_db'
        self.client = QdrantClient(path="cinesearch_db")
        self.collection_name = "video_frames"
        self._setup_collection()

    def _setup_collection(self):
        # Creates collection if it doesn't exist
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=512, distance=Distance.COSINE),
            )

    def add_frames(self, video_name, video_path, vectors, timestamps):
        """Saves embeddings and metadata to the database."""
        points = [
            PointStruct(
                id=str(uuid.uuid4()), # Unique ID for each frame
                vector=vec.tolist(),
                payload={"video_name": video_name, "path": video_path, "timestamp": ts}
            ) for vec, ts in zip(vectors, timestamps)
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_vector, limit=5):
        """Finds the most similar frames in the database."""
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=limit
        )