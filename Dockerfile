# Dockerfile


# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Playwright environment variables for Docker
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

# Set work directory
WORKDIR /app

# Install system dependencies including browser requirements
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    wget \
    gnupg \
    ca-certificates \
    xvfb \
    x11-utils \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo-gobject2 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libdrm2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    lsb-release \
    xdg-utils \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project to access fonts and other files
COPY . /app/

# Create logs directory
RUN mkdir -p /app/logs

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Install Playwright and browsers with dependencies as root
RUN pip install playwright==1.48.0

# Create fonts directory and copy custom fonts from static folder
RUN mkdir -p /usr/share/fonts/truetype/custom
RUN cp /app/bitbio/static/fonts/*.ttf /usr/share/fonts/truetype/custom/ 2>/dev/null || true
RUN cp /app/bitbio/static/fonts/*.otf /usr/share/fonts/truetype/custom/ 2>/dev/null || true
RUN cp /app/staticfiles/fonts/*.ttf /usr/share/fonts/truetype/custom/ 2>/dev/null || true
RUN cp /app/staticfiles/fonts/*.otf /usr/share/fonts/truetype/custom/ 2>/dev/null || true

# Update font cache
RUN fc-cache -f -v

# Install Playwright browsers with fallback approach
# Try to install Chromium browser, but don't fail the build if it doesn't work
RUN playwright install chromium || echo "Chromium installation failed, WeasyPrint will be used as fallback"

# Ensure Playwright browsers are accessible if they were installed
RUN chmod -R 755 /ms-playwright || true
RUN mkdir -p /home/appuser/.cache && chmod -R 755 /home/appuser/.cache

# Collect static files and set ownership
RUN python manage.py collectstatic --noinput
RUN chown -R appuser:appuser /app
RUN chmod -R 755 /app/logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
