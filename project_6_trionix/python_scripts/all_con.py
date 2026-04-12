from python_scripts import vector_embedding 
from python_scripts import youtube_downv3 as ytd
from python_scripts import extract_audio as ea
import os

ve = vector_embedding
def main(ytlink):
    yt_file=ytd.download_youtube_video(ytlink)
    audio_file=ea.main(yt_file)
    global loaded_sentences,loaded_embeddings,model
    loaded_sentences,loaded_embeddings,model=ve.main(audio_file)
    return loaded_sentences,loaded_embeddings,model

def main_from_file(file_path):
    """Process a locally uploaded file (MP4/WAV) instead of a YouTube link."""
    audio_file=ea.main(file_path)
    global loaded_sentences,loaded_embeddings,model
    loaded_sentences,loaded_embeddings,model=ve.main(audio_file)
    return loaded_sentences,loaded_embeddings,model


def myquery(query):
    try:
        return ve.myquery(query,loaded_sentences,loaded_embeddings,model)
    except NameError:
        print("Please run the main function first")
        return None
