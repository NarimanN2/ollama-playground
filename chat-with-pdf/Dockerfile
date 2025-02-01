
FROM python:3.11-slim


WORKDIR /app


COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY   /pdf_rag.py .


EXPOSE 8501

CMD ["streamlit", "run", "pdf_rag.py", "--server.enableCORS=false", "--server.port=8501"]
