import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('movie_reviews')

import nltk
import random
import string
import numpy as np

from nltk.corpus import movie_reviews
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import chi2
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

documents = [
    (movie_reviews.raw(fileid), category)
    for category in movie_reviews.categories()
    for fileid in movie_reviews.fileids(category)
]

random.shuffle(documents)
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = text.lower()
    text = "".join([char for char in text if char not in string.punctuation])
    words = nltk.word_tokenize(text)
    words = [word for word in words if word not in stop_words]
    return " ".join(words)

texts, labels = zip(*documents)
texts = [preprocess_text(text) for text in texts]
labels = np.array([1 if label == "pos" else 0 for label in labels])



X_train, X_test, y_train, y_test = train_test_split(
    texts,
    labels,
    test_size=0.2,
    random_state=42
)

vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

chi2_scores, p_values = chi2(X_train_tfidf, y_train)

top_k_features = np.argsort(chi2_scores)[-1000:]

X_train_selected = X_train_tfidf[:, top_k_features]
X_test_selected = X_test_tfidf[:, top_k_features]

classifier = MultinomialNB()
classifier.fit(X_train_selected, y_train)

y_pred = classifier.predict(X_test_selected)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

sample_text = ["The movie was absolutely fantastic I loved it!"]

sample_tfidf = vectorizer.transform(sample_text)[:, top_k_features]
prediction = classifier.predict(sample_tfidf)

print("Predicted Sentiment:", "Positive" if prediction[0] == 1 else "Negative")
