from pytubefix import YouTube
import os
# TODO: add audio download
def download_youtube_audio(link):
    yt = YouTube(link, 'ANDROID')
    print(yt.title)
    mypath=os.path.join(os.getcwd(),"project_6_trionix","data")
    audiopath=os.path.join(mypath,f"{yt.title}.mp3")
    ys = yt.streams.filter(only_audio=True).first()
    if not os.path.exists(audiopath) or (os.path.exists(audiopath) and os.path.getsize(audiopath) != ys.filesize):
        print("Downloading audio...")
        ys.download(mypath, filename=f"{yt.title}.mp3")
        print("Download completed!")
    else:
        print("File already exists!")
    return os.path.join(audiopath)
def download_youtube_video(link):
    yt = YouTube(link, 'ANDROID')
    print(yt.title)
    mypath=os.path.join(os.getcwd(),"project_6_trionix","data")
    vidpath=os.path.join(mypath,f"{yt.title}.mp4")
    ys = yt.streams.get_highest_resolution()
    if not os.path.exists(vidpath) or (os.path.exists(vidpath) and os.path.getsize(vidpath) != ys.filesize):
        print("Downloading...")
        ys.download(mypath)
        print("Download completed!")
    else:
        print("File already exists!")
    return str(os.path.join(vidpath))

# print(download_youtube_video("https://youtu.be/9ngnCrBKWZA?si=rEuk5WUIk-csKFNm"))
