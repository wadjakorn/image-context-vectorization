import torch
import numpy as np
from transformers import BlipProcessor, BlipForConditionalGeneration
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
from PIL import Image
from typing import List, Optional
import logging

from src.image_context_extractor.config.settings import ModelConfig


class ModelManager:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self._blip_processor = None
        self._blip_model = None
        self._clip_processor = None
        self._clip_model = None
        self._sentence_transformer = None

    @property
    def blip_processor(self):
        if self._blip_processor is None:
            model_path = self.config.local_blip_model_path or self.config.blip_model_name
            self.logger.info(f"Loading BLIP processor from: {model_path}")
            
            kwargs = self._get_loading_kwargs()
            self._blip_processor = BlipProcessor.from_pretrained(model_path, **kwargs)
        return self._blip_processor

    @property
    def blip_model(self):
        if self._blip_model is None:
            model_path = self.config.local_blip_model_path or self.config.blip_model_name
            self.logger.info(f"Loading BLIP model from: {model_path}")
            
            kwargs = self._get_loading_kwargs()
            self._blip_model = BlipForConditionalGeneration.from_pretrained(model_path, **kwargs)
            if self.config.device != "cpu":
                self._blip_model = self._blip_model.to(self.config.device)
        return self._blip_model

    @property
    def clip_processor(self):
        if self._clip_processor is None:
            model_path = self.config.local_clip_model_path or self.config.clip_model_name
            self.logger.info(f"Loading CLIP processor from: {model_path}")
            
            kwargs = self._get_loading_kwargs()
            self._clip_processor = CLIPProcessor.from_pretrained(model_path, **kwargs)
        return self._clip_processor

    @property
    def clip_model(self):
        if self._clip_model is None:
            model_path = self.config.local_clip_model_path or self.config.clip_model_name
            self.logger.info(f"Loading CLIP model from: {model_path}")
            
            kwargs = self._get_loading_kwargs()
            self._clip_model = CLIPModel.from_pretrained(model_path, **kwargs)
            if self.config.device != "cpu":
                self._clip_model = self._clip_model.to(self.config.device)
        return self._clip_model

    @property
    def sentence_transformer(self):
        if self._sentence_transformer is None:
            model_path = self.config.local_sentence_transformer_path or self.config.sentence_transformer_model
            self.logger.info(f"Loading Sentence Transformer from: {model_path}")
            
            kwargs = {}
            if self.config.cache_dir:
                kwargs['cache_folder'] = self.config.cache_dir
            
            self._sentence_transformer = SentenceTransformer(model_path, **kwargs)
        return self._sentence_transformer

    def _get_loading_kwargs(self) -> dict:
        """Get common kwargs for model loading"""
        kwargs = {}
        
        if self.config.cache_dir:
            kwargs['cache_dir'] = self.config.cache_dir
            
        if self.config.use_local_files_only:
            kwargs['local_files_only'] = True
            
        if self.config.trust_remote_code:
            kwargs['trust_remote_code'] = True
            
        return kwargs

    def generate_caption(self, image: Image.Image, max_length: int = 100, num_beams: int = 5) -> str:
        try:
            inputs = self.blip_processor(image, return_tensors="pt")
            if self.config.device != "cpu":
                inputs = {k: v.to(self.config.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                out = self.blip_model.generate(**inputs, max_length=max_length, num_beams=num_beams)
            
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            self.logger.error(f"Error generating caption: {e}")
            raise

    def extract_clip_features(self, image: Image.Image) -> np.ndarray:
        try:
            inputs = self.clip_processor(images=image, return_tensors="pt")
            if self.config.device != "cpu":
                inputs = {k: v.to(self.config.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
            
            return image_features.cpu().numpy().flatten()
        except Exception as e:
            self.logger.error(f"Error extracting CLIP features: {e}")
            raise

    def detect_objects(self, image: Image.Image, object_categories: List[str], threshold: float = 0.1) -> List[str]:
        try:
            inputs = self.clip_processor(
                text=object_categories, 
                images=image, 
                return_tensors="pt", 
                padding=True
            )
            if self.config.device != "cpu":
                inputs = {k: v.to(self.config.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            detected_objects = []
            for i, prob in enumerate(probs[0]):
                if prob > threshold:
                    detected_objects.append(object_categories[i])
            
            return detected_objects
        except Exception as e:
            self.logger.error(f"Error detecting objects: {e}")
            raise

    def create_embeddings(self, text: str) -> np.ndarray:
        try:
            embedding = self.sentence_transformer.encode(text)
            return embedding
        except Exception as e:
            self.logger.error(f"Error creating embeddings: {e}")
            raise