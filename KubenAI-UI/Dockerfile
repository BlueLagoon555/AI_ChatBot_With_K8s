# ===============================
# Build stage
# ===============================
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt



# ===============================
# Production image
# ===============================
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Copy Python deps
COPY --from=builder /root/.local /home/app/.local

WORKDIR /app

ENV PYTHONPATH=/app
ENV PATH=/home/app/.local/bin:$PATH

# Streamlit environment
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Copy project files
COPY src/ ./src/
COPY backend/ ./backend/
COPY docs/ ./docs/

# NOTE: Do NOT copy a .env into the image at build time.
# Environment variables should be provided at runtime (via docker-compose env_file or
# Docker environment) so secrets are not baked into the image.

# ✅ Remove default supervisor config
RUN rm -f /etc/supervisor/supervisord.conf

# ✅ Add main supervisor config (includes conf.d/*.conf)
COPY supervisord_main.conf /etc/supervisor/supervisord.conf

# ✅ Add program definitions (frontend + backend)
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN chown -R app:app /app /home/app/.local /etc/supervisor

USER app

# Expose API + UI ports
EXPOSE 8000
EXPOSE 8501

# ✅ Run supervisor in foreground mode
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]