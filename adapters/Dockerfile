FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

COPY adapters/requirements.txt /app/adapters/requirements.txt
RUN pip install --no-cache-dir -r /app/adapters/requirements.txt
RUN playwright install chromium --with-deps

COPY job-apply-mcp /app/job-apply-mcp
COPY adapters /app/adapters

EXPOSE 8001

CMD ["uvicorn", "adapters.server:app", "--host", "0.0.0.0", "--port", "8001"]
