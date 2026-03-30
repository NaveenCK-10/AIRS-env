FROM python:3.10-slim

WORKDIR /app

# Copy only requirements first (prevents pyproject interference)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the project
COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
