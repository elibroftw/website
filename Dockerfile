# Build stage for React app
FROM node:20-slim AS react-builder
WORKDIR /react-app
COPY react-app/package*.json ./
RUN npm install
COPY react-app/ .
RUN npm run build

# Final stage with AlmaLinux minimal
FROM almalinux:9-minimal

# Define build arguments for secrets
ARG SPOTIFY_CLIENT_ID
ARG SPOTIFY_SECRET
ARG COMMIT_SHA
ARG STRIPE_API_KEY
ARG SECRET_KEY
# Set environment variables
ENV SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID}
ENV SPOTIFY_SECRET=${SPOTIFY_SECRET}
ENV COMMIT_SHA=${COMMIT_SHA}
ENV STRIPE_API_KEY=${STRIPE_API_KEY}
ENV SECRET_KEY=${SECRET_KEY}
# Install Python and required system dependencies
RUN microdnf install -y python3 python3-pip

# Create symlinks for python and pip
RUN ln -sf /usr/bin/python3.9 /usr/bin/python && \
    ln -sf /usr/bin/pip3.9 /usr/bin/pip

# Add Python and pip binary locations to PATH
ENV PATH="/usr/local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy built React files from builder stage
COPY --from=react-builder /react-app/dist ./react-app/dist

# Copy application code (node_modules excluded via .dockerignore)
COPY . .

# Expose port 8000 (default for gunicorn)
EXPOSE 8000

# test if configured properly
RUN SERVER_ID=1 python -c "import app"

HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost:8000/ || exit 1

CMD ["gunicorn", "app:app"]
