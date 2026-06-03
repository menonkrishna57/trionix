from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
import requests
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

def transcribe(request):
    render(request, 'loader.html')
    try:
        # global loaded_sentences,loaded_embeddings,model
        user_query=request.GET['linkInput']
        print(f"transcribe view called with linkInput={user_query}")
        # ac.main now indexes the transcript into Qdrant and returns the number of indexed chunks
        indexed_count = ac.main(user_query)
        print(f"ac.main returned indexed_count={indexed_count}")
    except AttributeError:
        print("oh damn")
        indexed_count = 0
    return render(request, 'query.html', {'indexed_count': indexed_count})

def query(request):
    user_query=request.GET['myquery']
    print(f"query view received myquery={user_query}")
    res=ac.myquery(user_query)
    print(f"ac.myquery returned: {res}")
    return render(request, 'query.html',{'data': res})

def upload(request):
    global link
    link=request.GET['linkForm']
    global trans_path
    trans_path=youtube_downv3.download_youtube_video(link)
    transcribe(request)

def ytdownload(request):
    return render(request, 'youtube_downloader.html')
def audio(request):
    return render(request, 'audio_down.html')
def loading(request):
    return render(request, 'loader.html')