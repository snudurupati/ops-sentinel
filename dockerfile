# 1. Use Python 3.12-slim (Matches your dev environment)
FROM python:3.12-slim

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Set work directory
WORKDIR /app

# 4. Copy requirements first (caching layer)
COPY requirements.txt .

# 5. Install system dependencies
# We only strictly need 'build-essential' for compiling AI libraries and 'curl' for healthchecks
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 6. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy the application code
COPY . .

# 8. Expose Streamlit port
EXPOSE 8501

# 9. Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 10. Run the app
CMD ["streamlit", "run", "frontend/app.py", "--server.address=0.0.0.0"]