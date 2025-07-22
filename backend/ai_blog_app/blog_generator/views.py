from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
import os
import yt_dlp
import whisper
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from .models import BlogPost


# ✅ Configure Gemini API
genai.configure(api_key="")  # Replace with your actual key

# ✅ Whisper model (loads once globally)
whisper_model = whisper.load_model("base")  # options: "tiny", "base", "small", "medium", "large"

# ✅ Ensure FFmpeg is in PATH for Whisper
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\ffmpeg-2025-07-21-git-8cdb47e47a-essentials_build\bin"

# -----------------------------
# ✅ Main Views
# -----------------------------

@login_required
def index(request):
    return render(request, 'index.html')


@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data.get('link', '').strip()
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        if not yt_link or not yt_link.startswith("http"):
            return JsonResponse({'error': 'Invalid YouTube link'}, status=400)

        # ✅ Step 1: Fetch YouTube title
        try:
            title = yt_title(yt_link)
            if not title:
                return JsonResponse({'error': 'Could not fetch YouTube title'}, status=400)
        except Exception as e:
            print(f"Unexpected error fetching title: {e}")
            return JsonResponse({'error': 'Unexpected error fetching YouTube title'}, status=500)

        # ✅ Step 2: Get transcription (fallback to audio if needed)
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': "Failed to get transcript"}, status=500)

        # ✅ Step 3: Generate blog from transcript
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': "Failed to generate blog article"}, status=500)

        # ✅ Step 4: Save blog to DB
        new_blog_article = BlogPost.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=blog_content,
        )

        return JsonResponse({'content': blog_content}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# -----------------------------
# ✅ Helper Functions
# -----------------------------

def yt_title(link):
    """Fetch YouTube title using yt_dlp"""
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get('title')
    except Exception as e:
        print(f"Error fetching title with yt_dlp: {e}")
        return None


def get_transcription(link):
    """Try YouTubeTranscriptApi first, fallback to audio + Whisper"""
    try:
        # ✅ Get video_id from yt_dlp
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            video_id = info.get('id')

        transcript = None

        # ✅ Try English captions first
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            print("✅ Using YouTube English captions")
        except Exception:
            print("⚠️ English captions not available, trying other languages...")
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

                # ✅ Prefer generated transcripts first, then manually created
                first_transcript = (
                    next(iter(transcript_list._generated_transcripts.values()), None)
                    or next(iter(transcript_list._manually_created_transcripts.values()), None)
                )

                if first_transcript:
                    transcript = first_transcript.translate('en').fetch()
                    print("✅ Using translated non-English captions")
                else:
                    print("⚠️ No captions available at all.")
                    transcript = None
            except Exception:
                transcript = None

        if transcript:
            full_text = " ".join([t['text'] for t in transcript])
            return full_text

        # ✅ Fallback: Download audio and transcribe with Whisper
        print("⚠️ No captions found, downloading audio for Whisper...")
        audio_path = download_audio(link)
        if audio_path and os.path.exists(audio_path):
            print(f"✅ Whisper transcribing: {audio_path}")
            result = whisper_model.transcribe(audio_path)
            return result["text"]

        return None

    except Exception as e:
        print(f"❌ Error getting transcript: {e}")
        return None


def download_audio(link):
    try:
        output_path = settings.MEDIA_ROOT

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': True,
            'retries': 10,
            'nocheckcertificate': True,
            'ffmpeg_location': r"C:\ffmpeg\ffmpeg-2025-07-21-git-8cdb47e47a-essentials_build\bin"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info)

        # ✅ FIX: only replace spaces, not folder names
        folder, filename = os.path.split(file_path)
        new_filename = filename.replace(" ", "_")
        new_path = os.path.join(folder, new_filename)

        if file_path != new_path:
            os.rename(file_path, new_path)

        print(f"✅ Audio downloaded: {new_path}")
        return new_path

    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None





def generate_blog_from_transcription(transcription):
    """Generate blog article using Gemini (latest models)"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ Fast & free
        prompt = (
            f"Based on the following transcript from a YouTube video, "
            f"write a detailed, well-structured blog article. "
            f"Do not mention YouTube; make it read like a professional blog post:\n\n"
            f"{transcription}\n\nArticle:"
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating blog with Gemini: {e}")
        return None



# -----------------------------
# ✅ Blog Management Views
# -----------------------------

def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})


def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')


# -----------------------------
# ✅ Auth Views
# -----------------------------

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')


def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message': error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message': error_message})

    return render(request, 'signup.html')


def user_logout(request):
    logout(request)
    return redirect('/')
