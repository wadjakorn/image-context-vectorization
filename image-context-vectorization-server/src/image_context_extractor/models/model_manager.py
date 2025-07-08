import torch
import numpy as np
import time
from transformers import BlipProcessor, BlipForConditionalGeneration
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
from PIL import Image
from typing import List, Optional
import logging

from ..config.settings import ModelConfig


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
            self.logger.info(f"🔄 Loading BLIP processor from: {model_path}")
            start_time = time.time()
            
            kwargs = self._get_loading_kwargs()
            self._blip_processor = BlipProcessor.from_pretrained(model_path, **kwargs)
            
            load_time = time.time() - start_time
            self.logger.info(f"✅ BLIP processor loaded in {load_time:.2f} seconds")
        return self._blip_processor

    @property
    def blip_model(self):
        if self._blip_model is None:
            model_path = self.config.local_blip_model_path or self.config.blip_model_name
            self.logger.info(f"🔄 Loading BLIP model from: {model_path}")
            start_time = time.time()
            
            kwargs = self._get_loading_kwargs()
            self._blip_model = BlipForConditionalGeneration.from_pretrained(model_path, **kwargs)
            
            if self.config.device != "cpu":
                self.logger.info(f"🔄 Moving BLIP model to {self.config.device}")
                device_start = time.time()
                self._blip_model = self._blip_model.to(self.config.device)
                device_time = time.time() - device_start
                self.logger.info(f"✅ BLIP model moved to {self.config.device} in {device_time:.2f} seconds")
            
            load_time = time.time() - start_time
            self.logger.info(f"✅ BLIP model loaded in {load_time:.2f} seconds")
        return self._blip_model

    @property
    def clip_processor(self):
        if self._clip_processor is None:
            model_path = self.config.local_clip_model_path or self.config.clip_model_name
            self.logger.info(f"🔄 Loading CLIP processor from: {model_path}")
            start_time = time.time()
            
            kwargs = self._get_loading_kwargs()
            self._clip_processor = CLIPProcessor.from_pretrained(model_path, **kwargs)
            
            load_time = time.time() - start_time
            self.logger.info(f"✅ CLIP processor loaded in {load_time:.2f} seconds")
        return self._clip_processor

    @property
    def clip_model(self):
        if self._clip_model is None:
            model_path = self.config.local_clip_model_path or self.config.clip_model_name
            self.logger.info(f"🔄 Loading CLIP model from: {model_path}")
            start_time = time.time()
            
            kwargs = self._get_loading_kwargs()
            self._clip_model = CLIPModel.from_pretrained(model_path, **kwargs)
            
            if self.config.device != "cpu":
                self.logger.info(f"🔄 Moving CLIP model to {self.config.device}")
                device_start = time.time()
                self._clip_model = self._clip_model.to(self.config.device)
                device_time = time.time() - device_start
                self.logger.info(f"✅ CLIP model moved to {self.config.device} in {device_time:.2f} seconds")
            
            load_time = time.time() - start_time
            self.logger.info(f"✅ CLIP model loaded in {load_time:.2f} seconds")
        return self._clip_model

    @property
    def sentence_transformer(self):
        if self._sentence_transformer is None:
            model_path = self.config.local_sentence_transformer_path or self.config.sentence_transformer_model
            self.logger.info(f"🔄 Loading Sentence Transformer from: {model_path}")
            start_time = time.time()
            
            kwargs = {}
            if self.config.cache_dir:
                kwargs['cache_folder'] = self.config.cache_dir
            
            self._sentence_transformer = SentenceTransformer(model_path, **kwargs)
            
            load_time = time.time() - start_time
            self.logger.info(f"✅ Sentence Transformer loaded in {load_time:.2f} seconds")
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

    def preload_all_models(self) -> dict:
        """Preload all models and return timing information."""
        self.logger.info("🚀 Starting model preloading...")
        total_start = time.time()
        
        timings = {}
        
        # Load each model and track timing
        try:
            start = time.time()
            _ = self.sentence_transformer
            timings['sentence_transformer'] = time.time() - start
        except Exception as e:
            self.logger.error(f"❌ Failed to load Sentence Transformer: {e}")
            timings['sentence_transformer'] = None
        
        try:
            start = time.time()
            _ = self.blip_processor
            timings['blip_processor'] = time.time() - start
        except Exception as e:
            self.logger.error(f"❌ Failed to load BLIP processor: {e}")
            timings['blip_processor'] = None
        
        try:
            start = time.time()
            _ = self.blip_model
            timings['blip_model'] = time.time() - start
        except Exception as e:
            self.logger.error(f"❌ Failed to load BLIP model: {e}")
            timings['blip_model'] = None
        
        try:
            start = time.time()
            _ = self.clip_processor
            timings['clip_processor'] = time.time() - start
        except Exception as e:
            self.logger.error(f"❌ Failed to load CLIP processor: {e}")
            timings['clip_processor'] = None
        
        try:
            start = time.time()
            _ = self.clip_model
            timings['clip_model'] = time.time() - start
        except Exception as e:
            self.logger.error(f"❌ Failed to load CLIP model: {e}")
            timings['clip_model'] = None
        
        total_time = time.time() - total_start
        timings['total'] = total_time
        
        # Log summary
        self.logger.info(f"🎉 All models preloaded in {total_time:.2f} seconds")
        for model_name, load_time in timings.items():
            if load_time is not None and model_name != 'total':
                self.logger.info(f"   {model_name}: {load_time:.2f}s")
        
        return timings

    def get_model_status(self) -> dict:
        """Get current model loading status without triggering loads."""
        return {
            'blip_processor': self._blip_processor is not None,
            'blip_model': self._blip_model is not None,
            'clip_processor': self._clip_processor is not None,
            'clip_model': self._clip_model is not None,
            'sentence_transformer': self._sentence_transformer is not None,
        }

    def get_model_info(self) -> dict:
        """Get detailed model information including names and sources."""
        blip_path = self.config.local_blip_model_path or self.config.blip_model_name
        clip_path = self.config.local_clip_model_path or self.config.clip_model_name
        st_path = self.config.local_sentence_transformer_path or self.config.sentence_transformer_model
        
        def get_source_info(path):
            if path and ('/' in path and not path.startswith('/')):
                return {"name": path, "source": "Hugging Face Hub"}
            elif path and path.startswith('/'):
                return {"name": path.split('/')[-1], "source": f"Local: {path}"}
            else:
                return {"name": path or "Unknown", "source": "Unknown"}
        
        return {
            'blip': {
                **get_source_info(blip_path),
                'loaded': self._blip_model is not None and self._blip_processor is not None
            },
            'clip': {
                **get_source_info(clip_path),
                'loaded': self._clip_model is not None and self._clip_processor is not None
            },
            'sentence_transformer': {
                **get_source_info(st_path),
                'loaded': self._sentence_transformer is not None
            },
            'device': self.config.device
        }

    def generate_caption(self, image: Image.Image, max_length: int = 100, num_beams: int = 5, 
                        temperature: float = 0.7, repetition_penalty: float = 1.2) -> str:
        try:
            inputs = self.blip_processor(image, return_tensors="pt")
            if self.config.device != "cpu":
                inputs = {k: v.to(self.config.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                out = self.blip_model.generate(
                    **inputs, 
                    max_length=max_length, 
                    num_beams=num_beams,
                    temperature=temperature,
                    repetition_penalty=repetition_penalty,
                    do_sample=True
                )
            
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