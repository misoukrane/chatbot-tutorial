# chatbot-tutorial

## Setup
```bash
uv pip install -r requirements.txt
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
```

## Run Scraping
```bash
cd codereliant
scrapy crawl codereliant -L ERROR -O output.json
```

## Run the Chatbot
```bash
export OPEN_AI_API_KEY=your_openai_api_key
python chatbot.py
```