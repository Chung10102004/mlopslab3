FROM python:3.12

LABEL author="Chung"

WORKDIR /src

COPY model.pkl /src/model.pkl
COPY tfidf_vectorizer.pkl /src/tfidf_vectorizer.pkl
COPY sever.py /src/sever.py
COPY requirements.txt /src/requirements.txt


RUN pip install -r requirements.txt

EXPOSE 8888

CMD [ "uvicorn", "sever:app", "--host", "0.0.0.0", "--port", "8888"]
