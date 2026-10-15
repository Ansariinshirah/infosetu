"""Elasticsearch wrapper. If Elasticsearch is not running, every function
quietly does nothing and app.py falls back to SQLite LIKE search."""
import os
try:
    from elasticsearch import Elasticsearch
except ImportError:
    Elasticsearch = None

INDEX = "infosetu_requests"
es = None


def init():
    global es
    if Elasticsearch is None:
        return
    try:
        c = Elasticsearch(os.environ.get("ES_URL", "http://localhost:9200"), request_timeout=3)
        if c.ping():
            es = c
            print("[InfoSetu] Elasticsearch connected")
            return
    except Exception:
        pass
    print("[InfoSetu] Elasticsearch not available - using SQLite search")


def index(doc):
    if es:
        try:
            es.index(index=INDEX, id=doc["id"], document=doc, refresh=True)
        except Exception as e:
            print("ES index error:", e)


def search(q, user_id=None):
    """Return matching request ids, or None if ES is unavailable."""
    if not es:
        return None
    must = [{"multi_match": {"query": q, "fields": ["ref^3", "username", "full_name", "email", "category", "description", "dept"]}}]
    filt = [{"term": {"user_id": user_id}}] if user_id else []
    try:
        r = es.search(index=INDEX, query={"bool": {"must": must, "filter": filt}}, size=200)
        return [int(h["_id"]) for h in r["hits"]["hits"]]
    except Exception:
        return None
