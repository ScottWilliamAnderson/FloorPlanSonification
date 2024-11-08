FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy application code
COPY . .

# Install dependencies using uv
RUN uv pip install -r requirements.txt

# Expose the port where the app will run
EXPOSE 8000

# Run the application with uv
CMD ["uv", "run", "run.py"]