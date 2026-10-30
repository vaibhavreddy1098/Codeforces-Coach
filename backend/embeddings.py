from sklearn.feature_extraction.text import HashingVectorizer


_vectorizer = HashingVectorizer(
    n_features=384,
    alternate_sign=False,
    norm="l2",
    ngram_range=(1, 2),
    stop_words="english",
)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return _vectorizer.transform(texts).toarray().tolist()
