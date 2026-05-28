## Python Backend

This contains code to: 
1. Run the webscrapper to scrape parts from PartSelect website: 
    ```
    pip install -r requirements.txt
    cd webscrappers
    python parts_scrape.py
    ```
    To add more product types, run for product_url of the given type e.g 
    https://www.partselect.com/Refrigerator-Parts.htm and for 
    each repair page. 
    ScraperAPI key is needed to run webscrapper script (used to avoid Access Denied errors) Other scraper API tools can also be used. Create .env file
    based on .env.example provided. 

    Data files are in the `/webscrappers/data` folder in jsonl format. 

2. Load documents into ChromaDB vector database and start Microservice API 
to query database based on user query from frontend.

### To get python backend started
1. Start chroma db server: 
```
chroma run --host 0.0.0.0 --port 8000
```

2. Load documents into chroma (if documents have not been loaded previously)
```
python load_docs.py
```

3. Start FastAPI server (that frontend connects to):
```
uvicorn chroma_api:app --host 0.0.0.0 --port 8001 --reload
```

Server is setup when you see "Documents loaded into ChromaDB." (any calls before this will not work). Using `all-MiniLM-L6-v2` without chunking is very fast for set up. Using `all-mpnet-base-v2` with chunking takes about 20 mins for server to be up and running. 