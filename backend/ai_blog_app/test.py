# from pytube import YouTube
# yt = YouTube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
# print(yt.title)

# import yt_dlp
# with yt_dlp.YoutubeDL({}) as ydl:
#     info = ydl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
#     print(info.get('title'))

# from youtube_transcript_api import YouTubeTranscriptApi
# print(dir(YouTubeTranscriptApi))

from youtube_transcript_api import YouTubeTranscriptApi

video_id = "HcOc7P5BMi4"  # Python tutorial video
print(YouTubeTranscriptApi.list_transcripts(video_id))
