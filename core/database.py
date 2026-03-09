import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


class VectorDatabase:

    def __init__(self):
        self.client = QdrantClient(":memory:")
        self.collection_name = "vision_archive"

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=512,
                distance=Distance.COSINE
            )
        )

    def add_embeddings(self, embeddings, video_path, timestamps):
        points = []

        for emb, ts in zip(embeddings, timestamps):
            payload = {
                "video": video_path,
                "timestamp": ts
            }
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=emb.tolist(),
                payload=payload
            )
            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_vector, limit=5):
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            limit=limit
        )
        return results.points