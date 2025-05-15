# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install git for MCP SDK installation
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install MCP SDK directly from GitHub repository
RUN pip install git+https://github.com/modelcontextprotocol/python-sdk.git

# Install project Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code into container
COPY . .

EXPOSE 5050
EXPOSE 5080

# Command to run the server
# The container expects a volume mount at /pdfs for accessing local PDF files
# ENTRYPOINT ["python", "mcp_pdf_server.py"]
CMD ["sh", "-c", "python3 mcp_server/mcp_pdf_server.py & uvicorn manager_server.main:app --host 0.0.0.0 --port 5080"]
