from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import os
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
        loaded_sentences,loaded_embeddings,model=ac.main(user_query)
    except AttributeError:
        print("oh damn")
    return render(request, 'query.html')

def query(request):
    user_query=request.GET['myquery']
    res=ac.myquery(user_query)
    return render(request, 'query.html',{'data': res})

def upload(request):
    global link
    link=request.GET['linkForm']
    global trans_path
    trans_path=youtube_downv3.download_youtube_video(link)
    transcribe(request)

@csrf_exempt
def upload_file(request):
    """Handle uploaded video/audio files and process them through the ML pipeline."""
    if request.method == 'POST' and request.FILES.get('videoFile'):
        uploaded_file = request.FILES['videoFile']
        # Save the uploaded file to the data directory
        save_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, uploaded_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        try:
            loaded_sentences, loaded_embeddings, model = ac.main_from_file(file_path)
        except Exception as e:
            return HttpResponse(f"Error processing file: {e}", status=500)
        return render(request, 'query.html')
    return redirect('/')

def ytdownload(request):
    return render(request, 'youtube_downloader.html')
def audio(request):
    return render(request, 'audio_down.html')
def loading(request):
    return render(request, 'loader.html')