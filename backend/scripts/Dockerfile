FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scrape_tesda_nttc.py .

CMD ["python", "scrape_tesda_nttc.py"]
