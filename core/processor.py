import cv2
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

class VisionEngine:
    def __init__(self):
        # Using the base patch32 model for better performance on laptops
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def get_video_frames(self, video_path, sample_rate=2):
        """Extracts frames every 'sample_rate' seconds."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = []
        timestamps = []
        
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if count % int(fps * sample_rate) == 0:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(rgb_frame))
                timestamps.append(count / fps)
            count += 1
        cap.release()
        return frames, timestamps

    def encode_image_batch(self, images):
        """Generates embeddings for a list of images."""
        inputs = self.processor(images=images, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        return image_features.cpu().numpy()

    def encode_text(self, text):
        """Generates embedding for the search query."""
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        return text_features.cpu().numpy().flatten()