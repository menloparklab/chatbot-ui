FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0"]
CMD ["app:app"]
