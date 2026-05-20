from typing import Dict, List, Tuple
from config import HAS_SKLEARN
import streamlit as st
from datetime import datetime

if HAS_SKLEARN:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    import numpy as np

class MLPlagiarismClassifier:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.is_trained = False
        self.feature_names = [
            'type_agnostic_seq_sim', 'type_agnostic_jac_sim',
            'ted_sim', 'cfg_sim', 'winnowing_sim',
            'codebert_sim', 'bytecode_sim', 'big_o_match',
            'ast_sim', 'seq_sim', 'jac_sim', 'ngram_sim',
        ]

    def extract_features(self, result: Dict) -> np.ndarray:
        features = []
        for name in self.feature_names:
            features.append(result.get(name, 0))
        return np.array(features).reshape(1, -1)

    def train(self, training_data: List[Dict]):
        if not HAS_SKLEARN or len(training_data) < 10:
            return False
        X = []
        y = []
        for item in training_data:
            features = []
            for name in self.feature_names:
                features.append(item['features'].get(name, 0))
            X.append(features)
            y.append(item['label'])
        X = np.array(X)
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        self.model = DecisionTreeClassifier(
            max_depth=6,
            min_samples_split=3,
            min_samples_leaf=2,
            criterion='gini',
            random_state=42,
        )
        self.model.fit(X_scaled, y_encoded)
        self.is_trained = True
        return True

    def predict(self, result: Dict) -> Tuple[str, float]:
        if not self.is_trained or not HAS_SKLEARN:
            return None, 0.0
        features = self.extract_features(result)
        features_scaled = self.scaler.transform(features)
        pred_encoded = self.model.predict(features_scaled)[0]
        pred_label = self.label_encoder.inverse_transform([pred_encoded])[0]
        probas = self.model.predict_proba(features_scaled)[0]
        max_proba = max(probas) * 100
        return pred_label, max_proba


ml_classifier = MLPlagiarismClassifier()


def add_training_example(features: Dict, label: str):
    import streamlit as st
    from datetime import datetime
    
    st.session_state["training_data"].append({
        'features': features,
        'label': label,
        'timestamp': datetime.now().isoformat(),
    })
    if len(st.session_state["training_data"]) >= 10:
        if ml_classifier.train(st.session_state["training_data"]):
            st.sidebar.success(
                f"ML Model trained on {len(st.session_state['training_data'])} examples!"
            ) 
