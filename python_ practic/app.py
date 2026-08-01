import yt_dlp

url = input("Enter YouTube Video URL: ")

try:
    ydl_opts = {
        "format": "best",
        "outtmpl": "%(title)s.%(ext)s",
        "cookiesfrombrowser": ("chrome",),  # Chrome ki cookies use karega
        "quiet": False,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print("✅ Download Completed!")

except Exception as e:
    print("❌ Error:", e)   