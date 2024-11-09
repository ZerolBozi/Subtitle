import os
import re

import pysrt
from moviepy.editor import VideoFileClip
from faster_whisper import WhisperModel

def mp4_to_wav(video_path: str) -> str:
    safe_title = os.path.splitext(os.path.basename(video_path))[0]
    save_path = os.path.dirname(video_path)

    print(f"Converting MP4 to WAV... {safe_title}")
    video = VideoFileClip(video_path)
    new_path = os.path.join(save_path, f"{safe_title}.wav")
    video.audio.write_audiofile(new_path, codec='pcm_s16le')
    video.close()

    print(f"Converted MP4 to WAV OK!! {video_path}")
    print(f"safe_title:{safe_title}")

    return new_path

def transcribe_audio(video_path: str):
    model = WhisperModel("large-v2", device="cuda")
    segments, _ = model.transcribe(video_path, beam_size=5, initial_prompt="輸出為繁體中文")

    transcript = ""

    for i, segment in enumerate(segments, 1):
        start_hours, start_remainder = divmod(segment.start, 3600)
        start_minutes, start_seconds = divmod(start_remainder, 60)
        start_milliseconds = int((segment.start % 1) * 1000)
        end_hours, end_remainder = divmod(segment.end, 3600)
        end_minutes, end_seconds = divmod(end_remainder, 60)
        end_milliseconds = int((segment.end % 1) * 1000)

        transcript += "%d\n%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\n%s\n\n" % (
            i,
            start_hours, start_minutes, int(start_seconds), start_milliseconds,
            end_hours, end_minutes, int(end_seconds), end_milliseconds,
            segment.text
        )

    srt_path = video_path.replace(".wav", ".srt")

    print(f"SRT File at: {srt_path}")

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    srt_to_txt(srt_path)

def srt_to_txt(fileName: str):
    with open(os.path.join(f"{fileName}"), 'r', encoding='utf-8') as file:
        srt_content = file.read()

    cleaned_content = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', srt_content)
    cleaned_content = re.sub(r'\n\d+\n\n', '\n', cleaned_content).strip()
    cleaned_content = re.sub(r'\n+', '\n', cleaned_content).strip()

    filePath = os.path.dirname(fileName)
    file_base_name = os.path.splitext(os.path.basename(fileName))[0]
    with open(os.path.join(filePath,f"{file_base_name}.txt"), 'w', encoding='utf-8') as file:
        file.write(cleaned_content)

    print(f"數字和時間軸已移除，結果已儲存至{file_base_name}.txt檔案。")

def process_subtitle_index(srt_path: str):
    subs = pysrt.open(srt_path)

    for i, sub in enumerate(subs, start=1):
        sub.index = i

    subs.save(srt_path)

if __name__ == "__main__":
    # use
    video_path = os.getcwd() + "/test.mp4"
    wav_path = mp4_to_wav(video_path)

    transcribe_audio(wav_path)

    # process subtitle index
    # srt_path = "./test.srt"
    # process_subtitle_index(srt_path)