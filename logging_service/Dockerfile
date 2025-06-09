FROM ubuntu:latest

# Install the 'procps' package which includes 'top'
RUN apt-get update && apt-get install -y procps

# Set the command to run when the container starts
CMD ["top"]
FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001
CMD ["python", "app.py"]
