# Use the python:3.6 base image
FROM python:3.6

# Set the working directory
WORKDIR /app

# Copy the project files into the Docker image
COPY . /app

# Install the required dependencies using pip
RUN pip install --no-cache-dir -r reqs/requirements.txt

# Set the default command to run the app
CMD ["python", "run.py"]
