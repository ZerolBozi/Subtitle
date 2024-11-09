# Subtitle
A simple tool for automatically generating and embedding Chinese subtitles into videos using AI speech recognition. This project combines several packages to provide an integrated solution for video subtitle generation.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/ZerolBozi/Subtitle.git
cd Subtitle
```

2. Install Python packages:
```bash
# For CUDA 12+ users
pip install -r requirements.txt
```
```bash
# For CUDA 11 users
# First modify requirements.txt by uncommenting this line:
# ctranslate2==3.24.0
pip install -r requirements.txt
```

3. Install additional software based on your preferred method:
   - For using FFmpeg (Supports both GPU and CPU):
     - Download [FFmpeg](https://www.gyan.dev/ffmpeg/builds/) and note the installation path
   - For using moviepy (CPU only):
     - Download and install [ImageMagick](https://imagemagick.org/script/download.php)

## Basic Usage
1. First, generate subtitles from your video:
```python
from create_subtitle import mp4_to_wav, transcribe_audio
video_path = "./your_video.mp4"
wav_path = mp4_to_wav(video_path)
transcribe_audio(wav_path)
```

2. Then, embed the subtitles into your video:
```python
# Using FFmpeg (Supports both GPU and CPU)
from set_subtitle import set_subtitle_with_ffmpeg
video_path = "./your_video.mp4"
srt_path = "./your_video.srt"
ffmpeg_path = "C:/Program Files/ffmpeg/bin/ffmpeg.exe"  # Adjust this path

# For GPU encoding
set_subtitle_with_ffmpeg(
    video_path=video_path,
    srt_path=srt_path,
    ffmpeg_path=ffmpeg_path,
    device="gpu"  # default
)

# For CPU encoding
set_subtitle_with_ffmpeg(
    video_path=video_path,
    srt_path=srt_path,
    ffmpeg_path=ffmpeg_path,
    device="cpu"
)

# Or using moviepy (CPU only, slower)
from set_subtitle import set_subtitle_with_moviepy
from moviepy.config import change_settings
change_settings({
    "IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
})
set_subtitle_with_moviepy(video_path, srt_path)
```

## Notes
- Requires NVIDIA GPU for faster processing when using GPU mode
- Will generate these files in the same folder as your video:
  - `.wav` (temporary audio file)
  - `.srt` (subtitle file)
  - `.txt` (plain text transcription)
  - `_subtitle.mp4` (final video with subtitles)
- Default subtitle style is white text with black outline in Microsoft JhengHei font
- If there are errors in the subtitles:
  - You can manually edit the `.srt` file to correct any incorrect words
  - You can adjust the timing of subtitles by modifying the timestamp format in `.srt` file
    ```
    1
    00:00:01,000 --> 00:00:04,000
    Subtitle text here
    ```
