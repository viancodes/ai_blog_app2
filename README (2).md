# AI Blog App – YouTube to Blog Generator

## 📌 Overview
This is an **AI-powered Python Full-Stack Web App** that automatically converts **YouTube videos into professional blog articles**.  
It extracts transcripts (or transcribes audio using Whisper) and generates SEO-friendly blogs using **Google Gemini AI**.

---

## 🔧 Tech Stack
- **Backend:** Django (Python)  
- **Frontend:** HTML, CSS, JavaScript  
- **AI/ML:** Whisper (OpenAI), Gemini (Google Generative AI)  
- **Database:** PostgreSQL (Cloud-hosted on Render)  
- **Video Processing:** yt-dlp, FFmpeg  
- **Authentication:** Django Auth System  

---

## ✨ Key Features
✅ **Fetch YouTube Transcripts** using `YouTubeTranscriptApi`  
✅ **Fallback Transcription with Whisper AI** if captions aren’t available  
✅ **AI Blog Generation** via Gemini Pro (Google Generative AI)  
✅ **User Authentication** (Signup/Login, Django Auth)  
✅ **Stores Blogs in PostgreSQL** with User Association  
✅ **Production-Ready Django Architecture**  

---

## 🛠 Installation & Setup

### 1. Clone the Repo
```bash
git clone https://github.com/viancodes/ai_blog_app2.git
cd ai_blog_app2/backend
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv env
env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file inside `backend`:
```
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgres_url
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Go to: **http://127.0.0.1:8000**

---

## 🎯 How It Works
1. User logs in and provides a **YouTube link**.  
2. System fetches the transcript; if unavailable, it downloads the audio and uses **Whisper AI** to transcribe it.  
3. Transcript is passed to **Gemini AI** to generate a structured blog post.  
4. Blog is saved to **PostgreSQL** and listed for the logged-in user.

---

## 👤 Author
**Vishnu Vardan Babu Pentela**  
_Aspiring AI-based Python Full-Stack Developer_
