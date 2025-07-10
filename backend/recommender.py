# backend/recommender.py

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import nltk
from nltk.corpus import stopwords
from collections import Counter
# from nltk.downloader import DownloadError # <--- ELIMINAR ESTA LÍNEA
# import nltk.downloader as downloader # <--- ELIMINAR ESTA LÍNEA

# Asegúrate de que los recursos de NLTK estén descargados
try:
    nltk.data.find('corpora/stopwords')
except Exception: # <--- CAMBIO AQUÍ: Capturar una excepción más general
    nltk.download('stopwords')
    nltk.download('punkt') # Necesario para word_tokenize si lo usas en otro lugar

STOPWORDS = set(stopwords.words('spanish'))

def preprocess_text(text):
    """
    Limpia y tokeniza el texto.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text) # Elimina puntuación
    tokens = text.split() # Tokeniza por espacios
    tokens = [word for word in tokens if word not in STOPWORDS]
    return tokens

def tf(text_tokens):
    """
    Calcula la frecuencia de términos (TF) para un documento.
    text_tokens: Una lista de palabras (tokens) en el documento.
    """
    if not text_tokens:
        return {}
    counts = Counter(text_tokens)
    total_words = len(text_tokens)
    # Asegúrate de que 'vocab' sea una lista de palabras únicas para iterar
    vocab = list(counts.keys())
    # El error 'unhashable type: 'set'' sugiere que 'text_tokens' podría ser un set aquí.
    # Aseguramos que 'text_tokens' sea una lista para len() y que 'counts' se construya correctamente.
    return {word: counts[word] / total_words for word in vocab}


def idf(corpus):
    """
    Calcula la frecuencia inversa de documentos (IDF) para un corpus.
    corpus: Una lista de documentos, donde cada documento es una lista de palabras tokenizadas.
    """
    idf_values = {}
    num_documents = len(corpus)
    all_words = set(word for doc in corpus for word in doc)

    for word in all_words:
        count_docs_with_word = sum(1 for doc in corpus if word in doc)
        idf_values[word] = np.log(num_documents / (count_docs_with_word + 1)) + 1 # smoothed IDF

    return idf_values

def tfidf_vectorize(texts):
    """
    Vectoriza una lista de textos usando TF-IDF.
    texts: Una lista de cadenas de texto.
    """
    # Aseguramos que cada texto se preprocese a una lista de tokens
    processed_corpus = [preprocess_text(text) for text in texts]

    # Si hay un problema con la inicialización del vectorizador,
    # podemos usar la implementación de scikit-learn directamente si es posible.
    # Sin embargo, dado el error, parece que el problema está en la preparación de los datos.

    # Si la lista de textos está vacía, devuelve una lista vacía de vectores
    if not processed_corpus or all(not doc for doc in processed_corpus):
        return []

    # Unimos los tokens de cada documento en una sola cadena para TfidfVectorizer
    # TfidfVectorizer espera una lista de cadenas, no listas de tokens directamente.
    string_corpus = [" ".join(doc) for doc in processed_corpus]

    # Inicializa el TfidfVectorizer
    vectorizer = TfidfVectorizer(stop_words=list(STOPWORDS)) # Pasar la lista de stopwords
    tfidf_matrix = vectorizer.fit_transform(string_corpus)

    return tfidf_matrix.toarray()


def match_score(student_skills, vacant_requirements):
    """
    Calcula el score de compatibilidad entre las habilidades del estudiante y los requisitos de la vacante.
    student_skills: String con las habilidades del estudiante.
    vacant_requirements: String con los requisitos de la vacante.
    """
    if not student_skills or not vacant_requirements:
        return 0.0

    # Asegurarse de que ambos inputs sean strings
    student_skills_str = str(student_skills)
    vacant_requirements_str = str(vacant_requirements)

    texts = [student_skills_str, vacant_requirements_str]
    vectors = tfidf_vectorize(texts)

    if len(vectors) < 2:
        return 0.0 # No se pueden comparar si no hay al menos dos vectores

    # Calcula la similitud del coseno entre los dos vectores
    # cosine_similarity espera un array 2D, incluso para un solo par de vectores
    score = cosine_similarity(vectors[0].reshape(1, -1), vectors[1].reshape(1, -1))[0][0]
    return score
