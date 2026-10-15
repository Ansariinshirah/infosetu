# InfoSetu
Python (Flask) + SQLite + Elasticsearch (optional, auto-detected). English / Hindi / Marathi.

    python -m venv venv
    venv\Scripts\activate          (Windows)   |   source venv/bin/activate   (Mac/Linux)
    pip install -r requirements.txt
    python app.py                  -> http://127.0.0.1:5000

Admin login: admin / admin123 (set ADMIN_PASSWORD env var before first run to change).
Elasticsearch (optional): docker run -p 9200:9200 -e discovery.type=single-node -e xpack.security.enabled=false docker.elastic.co/elasticsearch/elasticsearch:8.15.0

## Request analyzer (analyzer.py)
Every new/edited request is checked before saving: text must be in the selected language only, long enough,
meaningful (no random letters / repeated words), related to the chosen department, with a valid name.
Duplicates and more than 5 requests per hour per user are blocked. Accepted requests get a quality score (admin view).
## Run
1. Start Elasticsearch 8.x (optional; search falls back to SQLite)
2. python -m venv venv, then venv\Scripts\activate
3. pip install -r requirements.txt
4. python app.py, then open http://127.0.0.1:5000

Set ADMIN_PASSWORD and SECRET_KEY environment variables before real use.
Debug mode is for local use only.