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

def search(request):
    context = {}
    # On form submission, a new video is transcribed and indexed
    if request.method == 'POST':
        video_link = request.POST.get('linkInput')
        if video_link:
            print(f"search view received POST with link: {video_link}")
            # Store the link in the session so we can query it later
            request.session['video_link'] = video_link
            
            # Show a loading screen/message while processing
            # For now, we process synchronously
            try:
                indexed_count = ac.main(video_link)
                print(f"ac.main returned indexed_count={indexed_count}")
                context['indexed_count'] = indexed_count
            except Exception as e:
                print(f"An error occurred during transcription/indexing: {e}")
                context['error'] = f"An error occurred: {e}"
        
        # After processing, render the query page
        return render(request, 'query.html', context)

    # On subsequent GET requests, we perform a search
    elif request.method == 'GET':
        user_query = request.GET.get('myquery')
        video_link = request.session.get('video_link') # Get link from session

        if user_query and video_link:
            print(f"search view received GET with query='{user_query}' for link='{video_link}'")
            try:
                # We assume ac.myquery uses the latest indexed data
                # If not, we might need to pass the video_link or an identifier to it
                results = ac.myquery(user_query)
                print(f"ac.myquery returned: {results}")
                context['data'] = results
                context['last_query'] = user_query
            except Exception as e:
                print(f"An error occurred during query: {e}")
                context['error'] = f"An error occurred during search: {e}"
        
        # If it's just a GET request to the page without a query, just show the page
        return render(request, 'query.html', context)

    # If it's not a GET or POST, redirect to home
    return redirect('/')

def ytdownload(request):
    return render(request, 'youtube_downloader.html')
def audio(request):
    return render(request, 'audio_down.html')
def loading(request):
    return render(request, 'loader.html')