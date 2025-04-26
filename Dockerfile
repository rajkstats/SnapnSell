FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD streamlit run --server.port $PORT --server.address 0.0.0.0 --server.enableCORS false app.py
