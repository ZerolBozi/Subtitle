import os
import re

import pysrt
from moviepy.editor import VideoFileClip
from faster_whisper import WhisperModel

def mp4_to_wav(video_path: str) -> str:
    """
    將 MP4 影片轉換成 WAV 音檔
    
    參數:
        video_path (str): MP4檔案的完整路徑
        
    回傳:
        str: 輸出的WAV檔案路徑
        
    用法:
        video_path = "./test.mp4"
        wav_path = mp4_to_wav(video_path)
        ### 輸出: ./test.wav
    """
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
    """
    使用 Whisper 模型將音檔轉換為繁體中文字幕
    
    參數:
        video_path (str): WAV檔案的完整路徑
        
    功能:
        - 使用 Whisper large-v2 模型進行語音識別
        - 自動輸出繁體中文字幕
        - 生成 SRT 格式字幕檔
        - 同時生成純文字檔案 (不含時間碼)
        
    用法:
        transcribe_audio("./test.wav")
        ### 會在相同目錄產生 .srt 和 .txt 檔案
    """
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
    """
    將 SRT 字幕檔轉換為純文字檔案
    
    參數:
        fileName (str): SRT檔案的完整路徑
        
    功能:
        - 移除時間碼標記
        - 移除字幕編號
        - 合併多餘的空行
        - 輸出純文字檔案
        
    用法:
        srt_to_txt("./test.srt")
        ### 輸出: ./test.txt
    """
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
    """
    重新處理 SRT 檔案的字幕編號，確保順序正確
    
    參數:
        srt_path (str): SRT檔案的完整路徑
        
    功能:
        - 修正字幕編號順序
        - 用於修改字幕後重新編號
        
    用法:
        process_subtitle_index("./test.srt")
    """
    subs = pysrt.open(srt_path)

    for i, sub in enumerate(subs, start=1):
        sub.index = i

    subs.save(srt_path)

if __name__ == "__main__":
   """
   操作流程:
   1. 先將影片轉成音檔
   2. 使用Whisper模型生成字幕檔
   3. 如果有修改字幕檔內容，最後可以重新排序字幕編號

   完整示範:
   """
   # 1. 指定影片路徑並轉換成WAV音檔
   video_path = os.getcwd() + "/test.mp4"
   wav_path = mp4_to_wav(video_path)

   # 2. 產生字幕檔 (.srt和.txt)
   transcribe_audio(wav_path)

   # 3. 如果有修改字幕，可以重新排序字幕編號 (選用)
   # srt_path = "./test.srt"
   # process_subtitle_index(srt_path)