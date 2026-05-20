from typing import Optional
from config import HAS_TRANSFORMERS, HAS_SKLEARN
import streamlit as st

if HAS_TRANSFORMERS:
    from transformers import AutoTokenizer, AutoModel
    import torch
if HAS_SKLEARN:
    import numpy as np

class CodeBERTAnalyzer:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self._loaded = False
        self._load_error = None

    def _load_model(self):
        if self._loaded:
            return True
        if not HAS_TRANSFORMERS:
            self._load_error = "transformers library not installed"
            return False
        try:
            model_name = "microsoft/codebert-base"
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name).to(self.device)
            self.model.eval()
            self._loaded = True
            return True
        except Exception as e:
            self._load_error = str(e)
            return False

    def encode(self, code: str) -> Optional[np.ndarray]:
        if not self._loaded and not self._load_model():
            return None
        try:
            if len(code) > 512:
                code = code[:512]
            inputs = self.tokenizer(
                code,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding="max_length",
            ).to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
                attention_mask = inputs['attention_mask'].unsqueeze(-1)
                masked_output = outputs.last_hidden_state * attention_mask
                summed = masked_output.sum(dim=1)
                counts = attention_mask.sum(dim=1)
                counts = torch.clamp(counts, min=1)
                embedding = (summed / counts).squeeze().cpu().numpy()
            return embedding
        except MemoryError:
            st.sidebar.error("CodeBERT: Out of memory")
            return None
        except Exception as e:
            st.sidebar.error(f"CodeBERT Error: {str(e)[:80]}")
            return None

    @staticmethod
    def cosine_similarity(vec_a, vec_b):
        if vec_a is None or vec_b is None:
            return 0.0
        try:
            norm_a = np.linalg.norm(vec_a)
            norm_b = np.linalg.norm(vec_b)
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return max(0.0, np.dot(vec_a, vec_b) / (norm_a * norm_b)) * 100
        except Exception:
            return 0.0

    def is_available(self):
        if self._loaded:
            return True
        return self._load_model()

    def get_status(self):
        if self._loaded:
            return "✅ CodeBERT ready"
        if self._load_error:
            return f"❌ {self._load_error[:100]}"
        return "⏳ CodeBERT not loaded"


codebert_analyzer = CodeBERTAnalyzer() 
