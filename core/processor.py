import cv2
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

class VisionEngine:
    def __init__(self):
        # Uses CUDA if you have an NVIDIA GPU, otherwise falls back to CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def get_video_frames(self, video_path, sample_rate=2):
        """Extracts one frame every 'sample_rate' seconds."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = []
        timestamps = []
        
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Logic to skip frames based on sample rate
            if count % int(fps * sample_rate) == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(rgb_frame))
                timestamps.append(count / fps)
            count += 1
        cap.release()
        return frames, timestamps

    def encode_image_batch(self, images):
        """Processes a list of images into vectors."""
        inputs = self.processor(images=images, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        return image_features.cpu().numpy()

    def encode_text(self, text):
        """Converts the user's search string into a vector."""
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        return text_features.cpu().numpy().flatten()