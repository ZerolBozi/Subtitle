import os
import subprocess

import pysrt
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip

def set_subtitle_with_moviepy(video_path: str, srt_path: str):
    """
    CPU Only

    速度很慢，不建議使用
    
    這個方法唯一的優點是字幕style可以更詳細的客製化
    """
    safe_title = os.path.splitext(os.path.basename(video_path))[0]

    video = VideoFileClip(video_path)
    subs = pysrt.open(srt_path)

    text_clips = []
    text_style = {
        'fontsize': 24,
        'color': 'white',
        'bg_color': 'black',
        'stroke_width': 1,
        'size': (video.w * 0.8, None)
    }

    for sub in subs:
        start_time = sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds + sub.start.milliseconds / 1000
        end_time = sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds + sub.end.milliseconds / 1000

        """
        TextClip(txt, 
                    font='Arial',                # 字體
                    fontsize=24,                 # 字體大小
                    color='white',               # 字體顏色
                    stroke_color='black',        # 描邊顏色
                    stroke_width=1,              # 描邊寬度
                    size=(video.w * 0.8, None))  # 寬度限制為影片寬度的 80%
            .set_position(('center', 'bottom'))  # 位置：置中，底部
            .margin(bottom=20)                   # 底部邊距 20 像素
            .set_duration(t_end - t_start)       # 持續時間
            .set_start(t_start))                 # 開始時間
        """
        text_clip = (TextClip(sub.text, **text_style)
                    .set_position(('center', 'bottom'))
                    .margin(bottom=20)
                    .set_duration(end_time - start_time)
                    .set_start(start_time))
        
        text_clips.append(text_clip)

    final_video = CompositeVideoClip([video] + text_clips)
    final_video.write_videofile(
        f"{safe_title}_subtitle.mp4",
        fps=video.fps,                 # 使用原影片的 fps
        codec='libx264',               # 使用 H.264 編碼
        audio_codec='aac',             # 音訊編碼
        threads=8,                     # 使用 8 個執行緒加速處理
        preset='ultrafast',            # 使用 ultrafast 預設設定
    )

def set_subtitle_with_ffmpeg(
        video_path: str, 
        srt_path: str, 
        ffmpeg_path: str, 
        device: str = "gpu",
        preset: str = "medium",
        bit_rate: str = "3M",
        style: list = None
    ):
    """
    使用 FFmpeg 為影片嵌入字幕，支援 GPU 加速編碼及自訂字幕樣式。
    
    功能:
        1. 將 .srt 格式字幕檔嵌入影片
        2. 支援 GPU (NVIDIA) 或 CPU 編碼
        3. 可自訂字幕樣式（大小、顏色、位置等）
        4. 可調整輸出影片品質及編碼速度
    
    參數:
        video_path (str): 輸入影片的完整路徑
        srt_path (str): 字幕檔(.srt)的完整路徑
        ffmpeg_path (str): FFmpeg 執行檔的完整路徑
        device (str, optional): 編碼裝置，可選 "gpu" 或 "cpu"。預設為 "gpu"
        preset (str, optional): 編碼速度設定，可選 "fast", "medium", "slow"。預設為 "medium"
            - fast: 編碼速度快，檔案較大
            - medium: 平衡速度與檔案大小
            - slow: 編碼速度慢，檔案較小
        bit_rate (str, optional): 輸出影片位元率，預設為 "3M"（3 Mbps）
            建議設定：
            - "1M": 適合 720p 或更低解析度
            - "2M": 適合 720p/1080p
            - "3M": 適合 1080p
            - "4M": 適合 1080p 高品質
            - "6M": 適合 1440p
            - "8M": 適合 4K
        style (list, optional): 字幕樣式設定清單，預設值為:
            [
                'FontName=Microsoft JhengHei',  # 字體
                'FontSize=14',                  # 字體大小
                'PrimaryColour=&HFFFFFF',       # 文字顏色(白色)
                'BackColour=&H00000000',        # 背景顏色(黑色)
                'BorderStyle=1',                # 背景樣式
                'Alignment=2',                  # 位置對齊(置中)
                'Outline=0.5',                  # 描邊寬度
                'MarginV=15',                   # 垂直邊距
            ]
    
    輸出:
        在影片同目錄下產生 "{原檔名}_subtitle.mp4" 的檔案
    
    使用範例:
        >>> # 基本使用
        >>> set_subtitle_with_ffmpeg(
        ...     video_path='C:/Videos/input.mp4',
        ...     srt_path='C:/Videos/subtitle.srt',
        ...     ffmpeg_path='C:/FFmpeg/ffmpeg.exe'
        ... )
        
        >>> # 自訂字幕樣式
        >>> custom_style = [
        ...     'FontName=Arial',
        ...     'FontSize=20',
        ...     'PrimaryColour=&HFF0000'  # 紅色文字
        ... ]
        >>> set_subtitle_with_ffmpeg(
        ...     video_path='C:/Videos/input.mp4',
        ...     srt_path='C:/Videos/subtitle.srt',
        ...     ffmpeg_path='C:/FFmpeg/ffmpeg.exe',
        ...     device='cpu',
        ...     preset='slow',
        ...     bit_rate='4M',
        ...     style=custom_style
        ... )
    """

    working_dir = os.path.dirname(os.path.abspath(video_path))
    os.chdir(working_dir)

    video_name = os.path.basename(video_path)
    srt_name = os.path.basename(srt_path)
    output_name = f"{os.path.splitext(video_name)[0]}_subtitle.mp4"
    
    """
    '-c:v'       # 視訊編碼器
    'h264_nvenc' # NVIDIA GPU 加速
    'libx264'    # CPU 編碼
    '-preset'    # 編碼速度 (ultrafast, fast, medium, slow)
    '-b:v'       # 視訊位元率
    '-c:a'       # 音訊編碼
    'copy'       # 直接複製原始音訊

    'FontSize'      # 字體大小
    'PrimaryColour' # 文字顏色
    'BackColour'    # 背景顏色
    'Outline'       # 描邊寬度
    'BorderStyle'   # 背景樣式
    'Alignment'     # 位置對齊
    'MarginV'       # 垂直邊距

    # 常見位元率設定
    '-b:v', '1M'    # 1 Mbps - 適合 720p 或更低解析度
    '-b:v', '2M'    # 2 Mbps - 適合 720p/1080p
    '-b:v', '3M'    # 3 Mbps - 適合 1080p
    '-b:v', '4M'    # 4 Mbps - 適合 1080p 高品質
    '-b:v', '6M'    # 6 Mbps - 適合 1440p
    '-b:v', '8M'    # 8 Mbps - 適合 4K

    presets = [
        'ultrafast',  # 最快，檔案最大，品質最差
        'superfast',
        'veryfast',
        'faster',
        'fast',      # 快速，檔案較大，品質尚可
        'medium',    # 預設值，平衡點
        'slow',
        'slower',
        'veryslow'   # 最慢，檔案最小，品質最好
    ]

    h264_nvenc 支援的 preset 選項：
        'p1' # 最快，品質最差
        'p2'
        'p3'
        'p4'
        'p5'
        'p6'
        'p7' # 最慢，品質最好

    # 或使用這些別名：
        'fast'          # 等同於 p1
        'medium'        # 等同於 p4
        'slow'          # 等同於 p7
        'lossless'      # 無損模式
        'default'       # 預設值
    """
    if style is None:
        style = [
            'FontName=Microsoft JhengHei',
            'FontSize=14',
            'PrimaryColour=&HFFFFFF',
            'BackColour=&H00000000',
            'BorderStyle=1',
            'Alignment=2',
            'Outline=0.5',      
            'MarginV=15',
        ]

    if device == "gpu":
        _device = 'h264_nvenc'
    else:
        _device = 'libx264'
    
    if preset not in ['fast', 'medium', 'slow']:
        preset = 'medium'

    cmd = [
        ffmpeg_path,
        '-i', video_name,
        '-vf', f'subtitles={srt_name}:force_style=\'' + ','.join(style) + '\'',
        '-c:v', _device,
        '-preset', preset,
        '-b:v', bit_rate,
        '-c:a', 'copy',
        output_name
    ]
    
    print(f"Executing command: {cmd}")

    process = subprocess.Popen(
        cmd, 
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    for line in process.stdout:
        print(line, end='')

if __name__ == "__main__":
   """
   操作流程:
   1. 設定影片和字幕檔案路徑
   2. 選擇使用哪種方式嵌入字幕:
       - moviepy: CPU處理，可以更詳細地客製化字幕樣式，但速度較慢
       - ffmpeg: 支援GPU加速，處理速度快，建議使用這個方式
   
   使用 moviepy 的情況:
   1. 需要先安裝 ImageMagick: https://imagemagick.org/script/download.php
   2. 設定 ImageMagick 路徑
   3. 呼叫 set_subtitle_with_moviepy 函數
   
   使用 ffmpeg 的情況 (推薦):
   1. 需要先安裝 FFmpeg: https://www.gyan.dev/ffmpeg/builds/
   2. 設定 FFmpeg 路徑 (可以設定環境變數或直接指定路徑)
   3. 呼叫 set_subtitle_with_ffmpeg 函數
   """
   
   # 1. 設定檔案路徑
   video_path = os.getcwd() + "\\test.mp4"
   srt_path = os.getcwd() + "\\test.srt"

   # 2-1. 使用 moviepy 方式 (CPU only)
   # from moviepy.config import change_settings
   # change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})
   # set_subtitle_with_moviepy(video_path, srt_path)

   # 2-2. 使用 ffmpeg 方式 (推薦，支援 GPU 加速)
   ffmpeg_path = r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"
   set_subtitle_with_ffmpeg(video_path, srt_path, ffmpeg_path)