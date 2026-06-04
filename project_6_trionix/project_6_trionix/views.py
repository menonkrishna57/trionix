from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
import requests
import re
from python_scripts import youtube_downv3
from python_scripts import all_con as ac

def home(request):
    return render(request, 'youtube_trans.html')


def login(request):
    return render(request, 'login/login.html')

def signup(request):
    return render(request, 'login/register_acc.html')

def download(request):


    try:
        link=request.GET['linkInput']
        file=youtube_downv3.download_youtube_video(link)
    except:
        pass
    print(file)


    response = FileResponse(open(file, 'rb'), as_attachment=True)
    print(response)
    response['Content-Disposition'] = f'attachment; filename="{file}"'
    return response

import mimetypes

...

def download_file(request):
    # fill these variables with real values
    fl_path = r"c:\Users\menon\Downloads"
    filename = "100+ Computer Science Concepts Explained.mp4"

    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response

def output(request):
    data=requests.get("https://reqres.in/api/users")
    print(data.text)
    return render(request, 'download.html', {'data': data.text}) 

# def transcribev1(request):
#     myobj=ve
#     res=None
#     try:
#         link=request.GET['linkInput']
#         print(link)
#         trans_path=youtube_downv3.download_youtube_video(link)
#         loaded_sentences,loaded_embeddings,model=myobj.main(trans_path)
#         res=myobj.myquery(trans_path,loaded_sentences,loaded_embeddings,model)

#     except AttributeError:
#         print("oh damn")

#     return render(request, 'query.html', {'data': res})

def search(request):
    context = {}
    # derive video_embed from any session-stored video_link (graceful if missing/invalid)
    def build_youtube_embed(link):
        if not link:
            return None
        m = re.search(r'(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})', link)
        if m:
            return f'https://www.youtube.com/embed/{m.group(1)}'
        if re.fullmatch(r'[A-Za-z0-9_-]{11}', link):
            return f'https://www.youtube.com/embed/{link}'
        return None

    session_video_link = request.session.get('video_link')
    if session_video_link:
        embed_url = build_youtube_embed(session_video_link)
        if embed_url:
            context['video_embed'] = embed_url

    # Accept both legacy GET submissions and newer POST submissions for indexing
    video_link = request.POST.get('linkInput') if request.method == 'POST' else request.GET.get('linkInput')
    if video_link:
        print(f"search view received {request.method} with link: {video_link}")
        request.session['video_link'] = video_link

        # compute embed for immediate render after storing in session
        embed_now = build_youtube_embed(video_link)
        if embed_now:
            context['video_embed'] = embed_now

        try:
            indexed_count = ac.main(video_link)
            print(f"ac.main returned indexed_count={indexed_count}")
            context['indexed_count'] = indexed_count
            # expose original video link for template use
            context['video_link'] = video_link
        except Exception as e:
            print(f"An error occurred during transcription/indexing: {e}")
            context['error'] = f"An error occurred: {e}"

        return render(request, 'query.html', context)

    # Handle query searches independently of whether a video_link is present in session
    user_query = request.GET.get('myquery')
    if user_query:
        print(f"search view received GET with query='{user_query}'")
        try:
            results = ac.myquery(user_query)
            print(f"ac.myquery returned: {results}")
            context['data'] = results
            context['last_query'] = user_query
            # pass through original source link if available in session
            context['video_link'] = request.session.get('video_link')
        except Exception as e:
            print(f"An error occurred during query: {e}")
            context['error'] = f"An error occurred during search: {e}"

    return render(request, 'query.html', context)

    # If it's not a GET or POST, redirect to home
    return redirect('/')

def ytdownload(request):
    return render(request, 'youtube_downloader.html')
def audio(request):
    return render(request, 'audio_down.html')
def loading(request):
    return render(request, 'loader.html')