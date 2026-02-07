"""
Quran Reels Generator - Android Compatible Video Generation Module
Replaces ImageMagick TextClip with Pillow-based text rendering for Android compatibility.
"""

import os
import sys
import shutil
import random
import logging
import traceback
import tempfile
import threading
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Audio processing
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

# Video processing
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, 
    concatenate_videoclips, ColorClip
)
import moviepy.video.fx.all as vfx

# Configure logging
def setup_logging(app_dir):
    log_path = os.path.join(app_dir, "runlog.txt")
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)
    return logging.getLogger()

# Path resolution for Android compatibility
def get_app_dir():
    """Returns the directory for external files (fonts, outputs, logs)"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_bundle_dir():
    """Returns the bundled temp directory or script dir for internal assets"""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

# Verse counts for each Surah
VERSE_COUNTS = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
    11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
    21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
    31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
    41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
    51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
    61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
    71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
    81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
    91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
    101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
    111: 5, 112: 4, 113: 5, 114: 6
}

# Surah names in Arabic
SURAH_NAMES = [
    'الفاتحة', 'البقرة', 'آل عمران', 'النساء', 'المائدة', 'الأنعام', 'الأعراف', 'الأنفال', 'التوبة', 'يونس',
    'هود', 'يوسف', 'الرعد', 'إبراهيم', 'الحجر', 'النحل', 'الإسراء', 'الكهف', 'مريم', 'طه',
    'الأنبياء', 'الحج', 'المؤمنون', 'النور', 'الفرقان', 'الشعراء', 'النمل', 'القصص', 'العنكبوت', 'الروم',
    'لقمان', 'السجدة', 'الأحزاب', 'سبأ', 'فاطر', 'يس', 'الصافات', 'ص', 'الزمر', 'غافر',
    'فصلت', 'الشورى', 'الزخرف', 'الدخان', 'الجاثية', 'الأحقاف', 'محمد', 'الفتح', 'الحجرات', 'ق',
    'الذاريات', 'الطور', 'النجم', 'القمر', 'الرحمن', 'الواقعة', 'الحديد', 'المجادلة', 'الحشر', 'الممتحنة',
    'الصف', 'الجمعة', 'المنافقون', 'التغابن', 'الطلاق', 'التحريم', 'الملك', 'القلم', 'الحاقة', 'المعارج',
    'نوح', 'الجن', 'المزمل', 'المدثر', 'القيامة', 'الإنسان', 'المرسلات', 'النبأ', 'النازعات', 'عبس',
    'التكوير', 'الانفطار', 'المطففين', 'الانشقاق', 'البروج', 'الطارق', 'الأعلى', 'الغاشية', 'الفجر', 'البلد',
    'الشمس', 'الليل', 'الضحى', 'الشرح', 'التين', 'العلق', 'القدر', 'البينة', 'الزلزلة', 'العاديات',
    'القارعة', 'التكاثر', 'العصر', 'الهمزة', 'الفيل', 'قريش', 'الماعون', 'الكوثر', 'الكافرون', 'النصر',
    'المسد', 'الإخلاص', 'الفلق', 'الناس'
]

# Reciters mapping
RECITERS_MAP = {
    'الشيخ عبدالباسط عبدالصمد': 'AbdulSamad_64kbps_QuranExplorer.Com',
    'الشيخ عبدالباسط عبدالصمد (مرتل)': 'Abdul_Basit_Murattal_64kbps',
    'الشيخ عبدالرحمن السديس': 'Abdurrahmaan_As-Sudais_64kbps',
    'الشيخ ماهر المعيقلي': 'Maher_AlMuaiqly_64kbps',
    'الشيخ محمد صديق المنشاوي (مجود)': 'Minshawy_Mujawwad_64kbps',
    'الشيخ سعود الشريم': 'Saood_ash-Shuraym_64kbps',
    'الشيخ مشاري العفاسي': 'Alafasy_64kbps',
    'الشيخ محمود خليل الحصري': 'Husary_64kbps',
    'الشيخ عبدالله الحذيفي': 'Hudhaify_64kbps',
    'الشيخ أبو بكر الشاطري': 'Abu_Bakr_Ash-Shaatree_128kbps',
    'الشيخ محمود علي البنا': 'mahmoud_ali_al_banna_32kbps'
}


class VideoGenerator:
    """Android-compatible video generator using Pillow instead of ImageMagick"""
    
    def __init__(self, app_dir=None, bundle_dir=None, progress_callback=None, log_callback=None):
        self.app_dir = app_dir or get_app_dir()
        self.bundle_dir = bundle_dir or get_bundle_dir()
        self.logger = setup_logging(self.app_dir)
        
        self.progress_callback = progress_callback or (lambda p, s: None)
        self.log_callback = log_callback or (lambda m: None)
        
        # Setup directories
        self.out_dir = os.path.join(self.app_dir, "outputs")
        self.audio_dir = os.path.join(self.out_dir, "audio")
        self.video_dir = os.path.join(self.out_dir, "video")
        self.font_dir = os.path.join(self.app_dir, "fonts")
        self.vision_dir = os.path.join(self.bundle_dir, "vision")
        
        # Font paths
        self.font_path = os.path.join(self.font_dir, "DUBAI-MEDIUM.TTF")
        self.font_path_arabic = os.path.join(self.font_dir, "DUBAI-BOLD.TTF")
        self.font_path_english = os.path.join(self.font_dir, "DUBAI-REGULAR.TTF")
        
        # Create directories
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)
        os.makedirs(self.font_dir, exist_ok=True)
        
        self.is_running = False
        self.should_stop = False
        
    def update_progress(self, percent, status):
        """Update progress with callback"""
        self.progress_callback(percent, status)
        
    def add_log(self, message):
        """Add log message with callback"""
        self.log_callback(message)
        self.logger.info(message)
        
    def detect_leading_silence(self, sound, thresh=-40, chunk=10):
        """Detect leading silence in audio"""
        t = 0
        while t < len(sound) and sound[t:t + chunk].dBFS < thresh:
            t += chunk
        return t

    def detect_trailing_silence(self, sound, thresh=-40, chunk=10):
        """Detect trailing silence in audio"""
        return self.detect_leading_silence(sound.reverse(), thresh, chunk)

    def download_audio(self, reciter_id, surah, ayah, idx):
        """Download and trim audio for a specific verse"""
        os.makedirs(self.audio_dir, exist_ok=True)
        fn = f'{surah:03d}{ayah:03d}.mp3'
        url = f'https://everyayah.com/data/{reciter_id}/{fn}'
        out = os.path.join(self.audio_dir, f'part{idx}.mp3')
        
        self.logger.info(f"Downloading audio from: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        
        with open(out, 'wb') as f:
            f.write(r.content)
        
        # Trim silence
        snd = AudioSegment.from_file(out, 'mp3')
        thresh = snd.dBFS - 16
        start = self.detect_leading_silence(snd, thresh)
        end = self.detect_trailing_silence(snd, thresh)
        trimmed = snd[start:len(snd) - end]
        trimmed.export(out, format='mp3')
        
        return out

    def get_ayah_text(self, surah, ayah):
        """Fetch Arabic text for a verse"""
        resp = requests.get(
            f'https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/quran-uthmani',
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()['data']['text']

    def wrap_text(self, text, per_line):
        """Wrap text into multiple lines"""
        words = text.split()
        lines = [' '.join(words[i:i + per_line]) for i in range(0, len(words), per_line)]
        return '\n'.join(lines)

    def render_text_to_image(self, text, width=900, video_height=1080):
        """
        Render Arabic text to transparent PNG using Pillow.
        Replaces MoviePy TextClip (which requires ImageMagick).
        """
        words = text.split()
        word_count = len(words)
        
        # Dynamic settings based on text length
        if word_count > 60:
            fontsize = 16
            per_line = 10
        elif word_count > 40:
            fontsize = 20
            per_line = 9
        elif word_count > 25:
            fontsize = 25
            per_line = 8
        elif word_count > 15:
            fontsize = 30
            per_line = 7
        else:
            fontsize = 35
            per_line = 6
        
        wrapped_text = self.wrap_text(text, per_line)
        
        # Load font
        try:
            font = ImageFont.truetype(self.font_path_arabic, fontsize)
        except Exception as e:
            self.logger.error(f"Failed to load font: {e}")
            # Fallback to default
            font = ImageFont.load_default()
        
        # Calculate text size
        dummy_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        # Get text bounding box
        bbox = dummy_draw.multilinebbox((0, 0), wrapped_text, font=font, align='center')
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Add padding
        padding = 40
        img_width = min(width, text_width + padding * 2)
        img_height = text_height + padding * 2
        
        # Create image with transparent background
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw text centered
        x = img_width // 2
        y = img_height // 2
        draw.multiline_text(
            (x, y),
            wrapped_text,
            font=font,
            fill=(255, 255, 255, 255),
            align='center',
            anchor='mm'
        )
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name, 'PNG')
        temp_file.close()
        
        return temp_file.name, fontsize

    def pick_background(self):
        """Select random background video"""
        try:
            files = [f for f in os.listdir(self.vision_dir) 
                    if f.startswith('nature_part') and f.endswith('.mp4')]
            if not files:
                raise ValueError("No background videos found in vision folder")
            return os.path.join(self.vision_dir, random.choice(files))
        except Exception as e:
            self.logger.error(f"Error picking background: {e}")
            raise

    def stop(self):
        """Signal to stop generation"""
        self.should_stop = True

    def generate_video(self, reciter_id, surah, start_ayah, end_ayah=None):
        """
        Main video generation method.
        Returns: (success: bool, output_path: str or None, error: str or None)
        """
        self.is_running = True
        self.should_stop = False
        output_path = None
        
        try:
            self.add_log('[1] Clearing output folders...')
            self.update_progress(5, 'جاري تنظيف ملفات الإخراج...')
            
            # Clear audio directory
            if os.path.isdir(self.audio_dir):
                shutil.rmtree(self.audio_dir)
                os.makedirs(self.audio_dir, exist_ok=True)
            
            max_ayah = VERSE_COUNTS[surah]
            
            # Determine end ayah
            if end_ayah is None:
                last_ayah = min(start_ayah + 9, max_ayah)
            else:
                last_ayah = min(end_ayah, max_ayah)
            
            if last_ayah < start_ayah:
                last_ayah = start_ayah
            
            total = last_ayah - start_ayah + 1
            
            self.add_log(f'[2] Preparing {total} verses (from {start_ayah} to {last_ayah})')
            self.update_progress(10, f'جاري تحضير {total} آيات...')
            
            clips = []
            temp_text_images = []
            
            for idx, ayah in enumerate(range(start_ayah, last_ayah + 1), start=1):
                if self.should_stop:
                    self.add_log('Generation stopped by user')
                    self.update_progress(0, 'تم الإلغاء')
                    return False, None, "Cancelled by user"
                
                progress_per_ayah = 70 / total
                base_progress = 10 + (idx - 1) * progress_per_ayah
                
                # Download audio
                self.add_log(f'[3.{idx}] Downloading audio for verse {ayah}')
                self.update_progress(
                    int(base_progress + progress_per_ayah * 0.3),
                    f'جاري تحميل صوت الآية {ayah}...'
                )
                audio_path = self.download_audio(reciter_id, surah, ayah, idx - 1)
                
                # Get text
                self.add_log(f'[3.{idx}] Fetching text')
                self.update_progress(
                    int(base_progress + progress_per_ayah * 0.5),
                    f'جاري جلب نص الآية {ayah}...'
                )
                arabic_text = self.get_ayah_text(surah, ayah)
                
                # Load audio to get duration
                audio_clip = AudioFileClip(audio_path).audio_fadein(0.2).audio_fadeout(0.2)
                duration = audio_clip.duration
                
                # Build segment
                self.add_log(f'[3.{idx}] Building segment')
                self.update_progress(
                    int(base_progress + progress_per_ayah * 0.8),
                    f'جاري إنشاء مقطع الآية {ayah}...'
                )
                
                # Background video
                bg_path = self.pick_background()
                bg_clip = VideoFileClip(bg_path)
                seg_bg = bg_clip.fx(vfx.loop, duration=duration).subclip(0, duration)
                
                # Text overlay using Pillow-rendered image
                text_img_path, _ = self.render_text_to_image(arabic_text)
                temp_text_images.append(text_img_path)
                
                text_clip = ImageClip(text_img_path).set_duration(duration)
                # Center the text
                text_clip = text_clip.set_position('center')
                
                # Composite
                seg = CompositeVideoClip([seg_bg, text_clip]).set_audio(audio_clip)
                clips.append(seg)
                
                # Clean up background clip
                bg_clip.close()
            
            # Concatenate
            self.add_log('[4] Concatenating segments...')
            self.update_progress(85, 'جاري دمج المقاطع...')
            final = concatenate_videoclips(clips, method='compose')
            
            # Generate output filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            surah_name = SURAH_NAMES[surah - 1]
            filename = f"QuranReel_{surah_name}_{start_ayah}-{last_ayah}_{timestamp}.mp4"
            output_path = os.path.join(self.video_dir, filename)
            
            self.add_log(f'[5] Writing final video → {output_path}')
            self.update_progress(90, 'جاري كتابة الفيديو النهائي...')
            
            final.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                audio_bitrate='192k',
                verbose=False,
                ffmpeg_params=['-movflags', '+faststart']
            )
            
            # Clean up clips
            for clip in clips:
                clip.close()
            final.close()
            
            # Clean up temp text images
            for temp_img in temp_text_images:
                try:
                    os.unlink(temp_img)
                except:
                    pass
            
            self.add_log('[6] Done!')
            self.update_progress(100, 'تم بنجاح!')
            
            return True, output_path, None
            
        except Exception as e:
            error_msg = f"Error in generate_video: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.add_log(f'[ERROR] {str(e)}')
            self.update_progress(0, f'خطأ: {str(e)}')
            return False, None, str(e)
            
        finally:
            self.is_running = False


# Convenience function for simple usage
def generate_quran_video(reciter_id, surah, start_ayah, end_ayah=None, 
                         progress_callback=None, log_callback=None):
    """
    Simple function to generate a Quran video.
    
    Args:
        reciter_id: Reciter ID from RECITERS_MAP values
        surah: Surah number (1-114)
        start_ayah: Starting verse number
        end_ayah: Ending verse number (optional, defaults to start+9)
        progress_callback: Function(percent, status) to call with progress updates
        log_callback: Function(message) to call with log messages
    
    Returns:
        tuple: (success: bool, output_path: str or None, error: str or None)
    """
    generator = VideoGenerator(
        progress_callback=progress_callback,
        log_callback=log_callback
    )
    return generator.generate_video(reciter_id, surah, start_ayah, end_ayah)
