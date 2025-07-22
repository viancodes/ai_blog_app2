from youtube_transcript_api import YouTubeTranscriptApi

video_id = "HcOc7P5BMi4"  # Example Python tutorial video

try:
    # ✅ Try English first
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    print("✅ English transcript found.")
except:
    print("⚠️ English not found, trying translation...")
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        # Pick first available generated transcript
        first_transcript = next(iter(transcript_list._generated_transcripts.values()))
        translated_transcript = first_transcript.translate('en').fetch()

        if translated_transcript:
            transcript = translated_transcript
            print("✅ Successfully translated to English.")
        else:
            print("⚠️ Translation returned empty data.")
            transcript = first_transcript.fetch()  # fallback to original language

    except Exception as e:
        print(f"❌ Translation failed: {e}")
        transcript = None

if transcript:
    full_text = " ".join([x['text'] for x in transcript])
    print("\nTranscript Sample:")
    print(full_text[:500])
else:
    print("❌ No transcript available.")
