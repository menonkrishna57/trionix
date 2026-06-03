from python_scripts import vector_embedding 
from python_scripts import youtube_downv3 as ytd
from python_scripts import extract_audio as ea
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
    transcript_file = ea.main(yt_file)
    logger.info("Transcript file created: %s", transcript_file)
    # use youtube filename or ytlink as source id
    source_id = os.path.splitext(os.path.basename(yt_file))[0]
    try:
        count = ve.index_transcript(transcript_file, source_id=source_id)
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
        return [f"{i+1}. {r['text']} (score={r['score']:.3f}, start={r.get('start')})" for i, r in enumerate(results)]
    except Exception as e:
        logger.exception("Query failed: %s", e)
        return None
