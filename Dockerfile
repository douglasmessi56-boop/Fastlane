FROM mcr.microsoft.com/playwright/python:v1.48.0-noble
WORKDIR /app
COPY . /app
RUN pip install playwright
EXPOSE 8099
CMD ["python3", "app.py"]
