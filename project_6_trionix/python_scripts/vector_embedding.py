import numpy as np 
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import json
from typing import List, Dict, Any, Optional

from python_scripts import qdrant_store
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

def load_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text
def preprocess_text(text):
    text = text.lower()  
    text = re.sub(r'\s+', ' ', text) 
    return text
def process_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text) 
    sentences = [preprocess_text(sentence) for sentence in sentences if sentence.strip()]
    return sentences

def generate_embeddings(sentences, model_name='all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences)
    return embeddings, model


def index_transcript(
    transcript_file: str,
    source_id: Optional[str] = None,
    collection: str = "trionix-transcripts",
    model_name: str = 'all-MiniLM-L6-v2',
    replace_collection: bool = False,
) -> int:
    """Index transcript into Qdrant. Uses transcript_segments.json if present; otherwise falls back to sentence splitting.

    Returns the number of points upserted.
    """
    # load segments if available
    seg_json = os.path.join(os.path.dirname(transcript_file), 'transcript_segments.json')
    segments = None
    if os.path.exists(seg_json):
        with open(seg_json, 'r', encoding='utf-8') as f:
            try:
                segments = json.load(f)
            except Exception:
                segments = None

    if segments:
        texts = [s.get('text','').strip() for s in segments if s.get('text','').strip()]
    else:
        text = load_transcript(transcript_file)
        texts = process_sentences(text)

    if not source_id:
        source_id = os.path.splitext(os.path.basename(transcript_file))[0]

    logger.info("Using %d chunks for indexing (source_id=%s)", len(texts), source_id)
    model = SentenceTransformer(model_name)
    logger.info("Generating embeddings using model %s...", model_name)
    embeddings = model.encode(texts)
    logger.info("Embeddings generated: shape=%s", getattr(embeddings, 'shape', None))

    vector_size = getattr(embeddings, 'shape', [None, None])[1]
    if replace_collection:
        logger.info("Replacing collection '%s' before indexing source_id=%s", collection, source_id)
        qdrant_store.recreate_collection(collection_name=collection, vector_size=vector_size)
    else:
        logger.info("Ensuring collection '%s' exists", collection)
        qdrant_store.ensure_collection(collection_name=collection, vector_size=vector_size)

    points = []
    for idx, vec in enumerate(embeddings):
        pid = qdrant_store._make_point_id(source_id, idx)
        payload = {
            'text': texts[idx],
            'source_id': source_id,
            'chunk_index': idx,
            'start': None,
            'end': None,
        }
        if segments and idx < len(segments):
            payload['start'] = segments[idx].get('start')
            payload['end'] = segments[idx].get('end')

        points.append({'id': pid, 'vector': vec.tolist(), 'payload': payload})

    # upsert
    logger.info("Prepared %d points for upsert (first_id=%s)", len(points), points[0]['id'] if points else None)
    qdrant_store.upsert_points(collection_name=collection, points=points)
    logger.info("Indexing complete for source_id=%s, points=%d", source_id, len(points))
    return len(points)


def search_qdrant(query: str, collection: str = "trionix-transcripts", model_name: str = 'all-MiniLM-L6-v2', top_n: int = 5) -> List[Dict[str, Any]]:
    logger.info("Search requested: '%s' (collection=%s, top_n=%d)", query, collection, top_n)
    model = SentenceTransformer(model_name)
    qvec = model.encode([query])[0]
    logger.info("Query vector generated (len=%d)", len(qvec))
    hits = qdrant_store.search(collection_name=collection, query_vector=qvec, top=top_n)
    # normalize hits to include text, score, start, end
    results = []
    for h in hits:
        payload = h.get('payload') or {}
        results.append({
            'text': payload.get('text'),
            'score': h.get('score'),
            'start': payload.get('start'),
            'end': payload.get('end'),
            'source_id': payload.get('source_id'),
        })
    logger.info("Search returned %d results", len(results))
    return results

def save_embeddings_and_sentences(embeddings, sentences, embeddings_file, sentences_file):
    np.save(embeddings_file, embeddings)
    with open(sentences_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(sentences))

def search_transcript(query, sentences, embeddings, model, top_n=5):
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = similarities.argsort()[-top_n:][::-1] 
    results = [(sentences[idx], similarities[idx]) for idx in top_indices]
    return results


def myquery(query,loaded_sentences,loaded_embeddings,model):
    # query = input("\nEnter your search query (or type 'exit' to quit): ")
    # if query.lower() == 'exit':
    #     print("Exiting...")
    #     return True
    
    print("\nSearching for relevant sentences...")
    results = search_transcript(query, loaded_sentences, loaded_embeddings, model)
    print(f"\nSearch results for query: '{query}'\n")
    the_results = []
    for i, (sentence, score) in enumerate(results, start=1):
        the_results.append(f"{i}. {sentence}")
    return the_results
def main(transcript_file):
    embeddings_file = os.path.join(os.getcwd(),'data','processed','transcript_embeddings.npy')
    sentences_file = os.path.join(os.getcwd(), 'data','processed','processed_transcript.txt')
   
    print("Loading and processing the transcript...")
    text = load_transcript(transcript_file)
    sentences = process_sentences(text)
    
    print("Generating embeddings...")
    embeddings, model = generate_embeddings(sentences)
    
    print("Saving embeddings and processed sentences...")
    save_embeddings_and_sentences(embeddings, sentences, embeddings_file, sentences_file)
    
    print("Loading saved embeddings and sentences...")
    loaded_embeddings = np.load(embeddings_file)
    with open(sentences_file, 'r', encoding='utf-8') as file:
        loaded_sentences = file.read().split('\n')
    print("Loaded",loaded_sentences)
    print("Loaded",loaded_embeddings)
    print("Loaded",model)
    return loaded_sentences,loaded_embeddings,model
    # while True:
    #     if(myquery(query,loaded_sentences,loaded_embeddings,model)):
    #         break

if __name__ == "__main__":
    main()
