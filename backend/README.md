# Backend

chatbot-ui backend using [FastAPI](https://github.com/tiangolo/fastapi), [LangChain](https://github.com/hwchase17/langchain)
and [Lanarky](https://github.com/ajndkr/lanarky).

## Setup Instructions

The backend code is built with Python 3.11. Follow the steps below
to get started.

1.  Create conda environment:

    ```bash
    conda create -n chatbot-ui python=3.11 -y
    conda activate chatbot-ui
    ```

    You can choose any other environment manager of your choice.

2.  Install dependencies:

    ```bash
    pip install -r requirements-dev.txt
    ```

    **Note**: All requirement files are generated using `pip-tools`.

## Usage

Run the app locally:

```bash
uvicorn app:app --reload
```

You can the Swagger UI at http://localhost:8000/docs.

Sample curl request:

```bash
curl -X 'POST' \
  'http://localhost:8000/chat' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer $OPENAI_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant"
    },
    {
      "role": "user",
      "content": "hello!"
    }
  ],
  "max_tokens": 1000,
  "temperature": 0
}'
```
