FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 8501

# Default command
CMD ["sh", "-c", "cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 & cd frontend && streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]
