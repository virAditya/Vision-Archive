import torch
import cv2
from PIL import Image
from transformers import CLIPProcessor, CLIPModel


class VisionProcessor:

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32"
        ).to(self.device)

        self.processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32"
        )

    def extract_frames(self, video_path, interval=0.4):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_interval = max(1, int(fps * interval))

        frames = []
        timestamps = []
        frame_id = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_id % frame_interval == 0:
                timestamp = frame_id / fps
                frames.append(frame)
                timestamps.append(timestamp)
            frame_id += 1

        cap.release()
        return frames, timestamps

    def encode_images(self, frames):
        images = [
            Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            for frame in frames
        ]

        inputs = self.processor(
            images=images,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)

        # get_image_features() may return an object or a tensor depending on version
        if hasattr(outputs, "pooler_output"):
            embeddings = outputs.pooler_output
        elif hasattr(outputs, "last_hidden_state"):
            embeddings = outputs.last_hidden_state[:, 0, :]
        else:
            embeddings = outputs  # already a tensor

        embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        return embeddings.cpu().numpy()

    def encode_text(self, text):
        inputs = self.processor(
            text=[text],
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.get_text_features(**inputs)

        # get_text_features() may return an object or a tensor depending on version
        if hasattr(outputs, "pooler_output"):
            embedding = outputs.pooler_output
        elif hasattr(outputs, "last_hidden_state"):
            embedding = outputs.last_hidden_state[:, 0, :]
        else:
            embedding = outputs  # already a tensor

        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        return embedding.cpu().numpy()[0]