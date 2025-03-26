##############################################################################################
ARG PYTHON_VERSION=3.10-slim-bullseye

##############################################################################################
# Stage Build
##############################################################################################
FROM python:${PYTHON_VERSION} AS build-image

LABEL company="ChainML"
LABEL stage="intermediate"

# Install system dependencies
RUN apt-get update && \
    apt-get -y install git ssh curl build-essential

# Install Rust and Cargo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# Setup ssh for private packages
RUN mkdir -p -m 0700 /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

# Copy requirements and source code
COPY requirements.txt .
COPY src ./src/

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN --mount=type=ssh \
    pip install --upgrade pip && \
    pip install -r requirements.txt

##############################################################################################
# Stage Runtime
##############################################################################################
FROM python:${PYTHON_VERSION} AS runtime-image

LABEL company="ChainML"
LABEL stage="final"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment and application files from build stage
COPY --from=build-image /opt/venv /opt/venv
COPY data /data
COPY src /src

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/src
ENV PYTHONUNBUFFERED=1
ENV FLASK_PORT=8888

# Set proper permissions
RUN chown -R appuser:appuser /data /src /opt/venv

WORKDIR /src
EXPOSE 8888

# Switch to non-root user
USER appuser

# Run the application with gunicorn with proper logging
CMD ["gunicorn", "--bind", "0.0.0.0:8888", "--log-level", "debug", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
