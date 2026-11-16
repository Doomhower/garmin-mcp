FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY garmin_mcp.py .
ENV GARMIN_TOKEN_CACHE_DIR=/tmp/garmin-mcp-tokens
EXPOSE 8091
ENTRYPOINT ["python", "garmin_mcp.py"]
