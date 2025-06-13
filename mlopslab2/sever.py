import logging
from logging.handlers import RotatingFileHandler
import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Histogram

# --- 1. CẤU HÌNH LOGGING ĐỂ GHI RA FILE ---
# Đường dẫn thư mục log bên trong container
LOG_DIR = "/src/logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file = f"{LOG_DIR}/app.log"

# Dùng RotatingFileHandler để file log không bị quá lớn (5MB/file, giữ 5 file)
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Lấy root logger và thêm handler
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO) # Đặt level cho root logger
root_logger.addHandler(file_handler)

# --- 2. TẢI MODEL VÀ VECTORIZER ---
try:
    with open('tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
except Exception as e:
    logging.critical(f"Lỗi nghiêm trọng khi tải model hoặc vectorizer: {e}", exc_info=True)
    raise RuntimeError(f"Lỗi khi load model/vectorizer: {e}")

# --- 3. KHỞI TẠO ỨNG DỤNG VÀ MONITORING ---
app = FastAPI()

# Tạo các custom metrics cho model
MODEL_INFERENCE_TIME = Histogram('model_inference_latency_seconds', 'Thời gian dự đoán của model (giây)')
MODEL_CONFIDENCE_SCORE = Histogram('model_prediction_confidence', 'Độ tin cậy của dự đoán model')

# Gắn instrumentator vào app để tự động theo dõi API
Instrumentator().instrument(app).expose(app)

# --- 4. ĐỊNH NGHĨA CÁC ENDPOINTS ---
class InputData(BaseModel):
    features: str

@app.get("/")
def read_root():
    return {"message": "ML API is running"}

@app.post("/predict")
def predict(input: InputData):
 #   raise Exception("This is a deliberate test to trigger a 500 error!")
    try:
        text = input.features
        logging.info(f"Received prediction request for text: '{text}'")

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input must be a non-empty string.")

        # Vector hóa input
        X = vectorizer.transform([text])
        logging.info("Input vectorized successfully.")

        # Bắt đầu đo lường model
        start_time = time.perf_counter()

        # Dự đoán và lấy độ tin cậy
        try:
            probabilities = model.predict_proba(X)
            prediction = np.argmax(probabilities[0])
            confidence = np.max(probabilities[0])
        except AttributeError:
            prediction = model.predict(X)[0]
            confidence = 1.0
            logging.warning("Model không có 'predict_proba'. Confidence score được đặt là 1.0.")

        end_time = time.perf_counter()
        inference_time = end_time - start_time

        # Ghi nhận metrics
        MODEL_INFERENCE_TIME.observe(inference_time)
        MODEL_CONFIDENCE_SCORE.observe(confidence)
        logging.info(f"Prediction successful. Result: {prediction}, Confidence: {confidence:.4f}, Latency: {inference_time:.4f}s")

        return {"prediction": int(prediction), "confidence": float(confidence)}

    except ValueError as e:
        logging.warning(f"Bad request received: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"An unexpected error occurred during prediction: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
