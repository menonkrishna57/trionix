from python_scripts import vector_embedding 
from python_scripts import youtube_downv3 as ytd
from python_scripts import extract_audio as ea
from python_scripts import qdrant_store
import os
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

ve = vector_embedding


def main(ytlink):
    """Download video, transcribe, and index into Qdrant. Returns number of indexed chunks."""
    logger.info("all_con.main called with ytlink=%s", ytlink)
    yt_file = ytd.download_youtube_video(ytlink)
    logger.info("Downloaded youtube file: %s", yt_file)
    # use youtube filename or ytlink as source id
    source_id = os.path.splitext(os.path.basename(yt_file))[0]

    current_source_ids, current_point_count = qdrant_store.get_source_summary()
    if current_source_ids == {source_id} and current_point_count > 0:
        logger.info(
            "Qdrant already contains only source_id=%s (%d points); skipping re-index",
            source_id,
            current_point_count,
        )
        return current_point_count

    transcript_file = ea.main(yt_file)
    logger.info("Transcript file created: %s", transcript_file)

    try:
        count = ve.index_transcript(transcript_file, source_id=source_id, replace_collection=True)
        logger.info("Indexed %d chunks for source_id=%s", count, source_id)
        return count
    except Exception as e:
        logger.exception("Indexing failed: %s", e)
        return 0


def myquery(query):
    logger.info("all_con.myquery called: %s", query)
    try:
        results = ve.search_qdrant(query)
        logger.info("Query returned %d results", len(results))
        # Return a list of structured dicts for each hit
        structured = []
        for i, r in enumerate(results):
            structured.append({
                'rank': i + 1,
                'text': r.get('text'),
                'score': float(r.get('score')) if r.get('score') is not None else None,
                'start': r.get('start'),
                'source_id': r.get('source_id')
            })
        return structured
    except Exception as e:
        logger.exception("Query failed: %s", e)
        return None
