FROM python:3.12-slim

WORKDIR /app

# Install dependencies required for asyncpg or bcrypt if needed
RUN apt-get update && apt-get install -y gcc libffi-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Do not copy code here if mounting volume for hot-reload in dev
# but for completeness, we copy it.
COPY . .

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
