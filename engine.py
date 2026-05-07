# engine.py
import ast, tokenize, io, keyword, re
import numpy as np
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CodePlagiarismDetector:
    def __init__(self):
        pass
    
    def remove_comments(self, code):
        code = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\')', '', code, flags=re.DOTALL)
        code = re.sub(r'#.*', '', code)
        return code
    
    def get_token_string(self, code):
        tokens = tokenize.generate_tokens(io.StringIO(code).readline)
        meaningful = []
        for tok in tokens:
            if tok.type in {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                           tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING,
                           tokenize.ENDMARKER}:
                continue
            if tok.type == tokenize.NAME and not keyword.iskeyword(tok.string):
                meaningful.append('VAR')
            else:
                meaningful.append(tok.string)
        return ' '.join(meaningful)
    
    def get_ast_signature(self, code):
        tree = ast.parse(code)
        seq = []
        def traverse(node):
            seq.append(type(node).__name__)
            for child in ast.iter_child_nodes(node):
                traverse(child)
        traverse(tree)
        return ' '.join(seq)
    
    def analyze(self, codes, filenames, weights=(0.4, 0.6)):
        n = len(codes)
        clean = [self.remove_comments(c) for c in codes]
        token_strs = [self.get_token_string(c) for c in clean]
        
        vec = TfidfVectorizer(ngram_range=(1,3))
        tfidf = vec.fit_transform(token_strs)
        text_sim = cosine_similarity(tfidf)
        
        ast_sigs = [self.get_ast_signature(c) for c in codes]
        struct_sim = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                struct_sim[i][j] = SequenceMatcher(None, ast_sigs[i], ast_sigs[j]).ratio()
        
        final_sim = weights[0] * text_sim + weights[1] * struct_sim
        
        pairs = []
        for i in range(n):
            for j in range(i+1, n):
                pairs.append({
                    'file1': filenames[i],
                    'file2': filenames[j],
                    'text_similarity': round(text_sim[i][j]*100, 2),
                    'structure_similarity': round(struct_sim[i][j]*100, 2),
                    'final_similarity': round(final_sim[i][j]*100, 2),
                    'severity': 'high' if final_sim[i][j] > 0.7 else 'medium' if final_sim[i][j] > 0.4 else 'low'
                })
        
        return {
            'filenames': filenames,
            'n_files': n,
            'final_similarity': final_sim,
            'pairs': sorted(pairs, key=lambda x: x['final_similarity'], reverse=True),
            'statistics': {
                'total_pairs': n*(n-1)//2,
                'high_similarity': sum(1 for p in pairs if p['severity']=='high'),
                'medium_similarity': sum(1 for p in pairs if p['severity']=='medium'),
                'low_similarity': sum(1 for p in pairs if p['severity']=='low'),
                'avg_similarity': round(np.mean(final_sim[np.triu_indices(n, k=1)])*100, 2) if n>1 else 0
            }
        }