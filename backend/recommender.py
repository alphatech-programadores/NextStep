import numpy as np
import re
from collections import Counter
from math import log


# recommender.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def preprocess_text(text):
    if not text:
        return []
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  
    return text.split()


def tfidf_vectorize(texts):
    all_tokens = [preprocess_text(t) for t in texts]
    vocab = list(set(token) for tokens in all_tokens for token in tokens)

    def tf(text_tokens):
        counts = Counter(text_tokens)
        return np.array([counts[word] / len(text_tokens) for word in vocab])

    def idf():
        df = np.array([sum(1 for tokens in all_tokens if word in tokens) for word in vocab])
        return np.log(len(all_tokens) / (df + 1))
    
    idf_values = idf()
    vectors = []
    for tokens in all_tokens:
        vectors.append(tf(tokens) * idf_values)
    return np.array(vectors)


def cosine_similarity(vect1, vect2):
    num = np.dot(vect1, vect2)
    denom = np.linalg.norm(vect1) * np.linalg.norm(vect2)
    if denom == 0:
        return 0.0 # :)
    return float(num / denom)


def match_score(student_skills, vacant_requirements):
    # Preprocesar ambos textos
    texts = [student_skills, vacant_requirements]
    vectors = tfidf_vectorize(texts)
    return round(cosine_similarity(vectors[0], vectors[1], 4))