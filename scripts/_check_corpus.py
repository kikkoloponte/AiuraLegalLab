"""Script temporaneo per analisi corpus dettagliata."""
import asyncio
from aiura_legal.ingestion.mongodb.client import MongoClient

async def check():
    client = MongoClient()
    db = client.db
    chunks = db['chunks']

    total = await chunks.count_documents({})
    print(f"Chunks totali: {total}")

    # Distribuzione campo corpus (campo diretto)
    print("\n--- Valori campo 'corpus' ---")
    pipeline = [
        {"$group": {"_id": "$corpus", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    async for doc in chunks.aggregate(pipeline):
        print(f"  corpus='{doc['_id']}': {doc['count']}")

    # Distribuzione campo metadata.corpus
    print("\n--- Valori campo 'metadata.corpus' ---")
    pipeline2 = [
        {"$group": {"_id": "$metadata.corpus", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    async for doc in chunks.aggregate(pipeline2):
        print(f"  metadata.corpus='{doc['_id']}': {doc['count']}")

    # Quanti senza corpus?
    no_corpus = await chunks.count_documents({"corpus": {"$exists": False}})
    print(f"\nSenza campo 'corpus': {no_corpus}")

    # source_id prefix distribution
    print("\n--- Prefissi source_id (top 10) ---")
    pipeline3 = [
        {"$project": {"prefix": {"$substr": ["$source_id", 0, 20]}}},
        {"$group": {"_id": "$prefix", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    async for doc in chunks.aggregate(pipeline3):
        print(f"  '{doc['_id']}...': {doc['count']}")

    # Esempio chunk giurisprudenziale (se esiste)
    giuri_doc = await chunks.find_one({"source_id": {"$regex": "^giurisprudenza"}})
    if giuri_doc:
        print("\n--- Esempio chunk giurisprudenza ---")
        for k, v in giuri_doc.items():
            if k != '_id':
                print(f"  {k}: {str(v)[:100]}")
    else:
        print("\nNessun chunk con source_id che inizia per 'giurisprudenza'")

asyncio.run(check())
