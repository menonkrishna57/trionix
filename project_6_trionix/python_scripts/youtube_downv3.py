import yt_dlp
import os

def download_youtube_audio(link):
    mypath = os.path.join(os.getcwd(), "project_6_trionix", "data")
    os.makedirs(mypath, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(mypath, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        # Use prepare_filename to get the actual sanitized filename yt-dlp used
        filepath = ydl.prepare_filename(info)
        # Change extension to .mp3 since we postprocess to mp3
        audiopath = os.path.splitext(filepath)[0] + '.mp3'
        print("Download completed!")
        return audiopath

def download_youtube_video(link):
    mypath = os.path.join(os.getcwd(), "project_6_trionix", "data")
    os.makedirs(mypath, exist_ok=True)

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': os.path.join(mypath, '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        # Use prepare_filename to get the actual sanitized filename yt-dlp used
        vidpath = ydl.prepare_filename(info)
        print("Download completed!")
        return str(vidpath)

# print(download_youtube_video("https://youtu.be/9ngnCrBKWZA?si=rEuk5WUIk-csKFNm"))
