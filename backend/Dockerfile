FROM python:3.12-slim

WORKDIR /app

# Copy everything in current context (backend folder)
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Start Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
