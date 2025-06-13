import pandas as pd
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
vectorizer = pickle.load(open('tfidf_vectorizer.pkl', 'rb'))
input = vectorizer.transform(["I am a software engineer. I am looking for a job."])
print(model.predict(input))