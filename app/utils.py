from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def check_duplicate_blog(new_content, existing_contents):
    documents = [new_content] + existing_contents

    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform(documents)

    similarity_matrix = cosine_similarity(vectors)

    similarities = similarity_matrix[0][1:]

    max_similarity = max(similarities) if similarities.any() else 0

    return max_similarity   # return score instead of True/False