FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y python3-distutils

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"] 

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port=${PORT:-8000}"]
