import re
from typing import List, Set

class WinnowingFingerprint:
    def __init__(self, k: int = 5, window_size: int = 4):
        self.k = k
        self.window_size = window_size

    def _kgrams(self, text: str) -> List[str]:
        return [text[i:i + self.k] for i in range(len(text) - self.k + 1)]

    def _hash_kgram(self, kgram: str) -> int:
        return hash(kgram) & 0xFFFFFFFF

    def generate_fingerprint(self, code: str) -> Set[int]:
        normalized = re.sub(r'\s+', ' ', code).strip()
        kgrams = self._kgrams(normalized)
        if len(kgrams) < self.window_size:
            return set()
        hashes = [self._hash_kgram(kg) for kg in kgrams]
        fingerprint = set()
        for i in range(len(hashes) - self.window_size + 1):
            window = hashes[i:i + self.window_size]
            fingerprint.add(min(window))
        return fingerprint

    @staticmethod
    def compare_fingerprints(fp_a: Set[int], fp_b: Set[int]) -> float:
        if not fp_a or not fp_b:
            return 0.0
        intersection = len(fp_a & fp_b)
        union = len(fp_a | fp_b)
        return (intersection / union) * 100 if union > 0 else 0.0


winnowing_engine = WinnowingFingerprint(k=6, window_size=4) 
