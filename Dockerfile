FROM python:3.11-slim

WORKDIR /app

# Copy the template server into the image
COPY devkit/python-server-template/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Use `config.prod.json` if present, otherwise fall back to `config.sample.json`
RUN if [ -f /app/config.prod.json ]; then \
      cp /app/config.prod.json /app/config.json; \
    else \
      cp /app/config.sample.json /app/config.json; \
    fi

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
