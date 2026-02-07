"""
Quran Reels Generator - Kivy Android App
Native Python UI for Android using Kivy framework.
Replaces the Flask+HTML interface with a mobile-native interface.
"""

import os
import sys
import threading
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import platform

# Import our generator module
from generator import (
    VideoGenerator, RECITERS_MAP, SURAH_NAMES, 
    VERSE_COUNTS, get_app_dir, get_bundle_dir
)

# Colors matching original UI theme
COLORS = {
    'bg_dark': [0.11, 0.01, 0.11, 1],  # #1c031d
    'bg_secondary': [0.07, 0.07, 0.11, 1],  # #12121d
    'gold': [0.83, 0.69, 0.22, 1],  # #d4af37
    'gold_light': [0.96, 0.82, 0.44, 1],  # #f4d06f
    'text_primary': [1, 1, 1, 1],
    'text_secondary': [1, 1, 1, 0.7],
    'success': [0.29, 0.87, 0.5, 1],  # #4ade80
    'error': [0.97, 0.44, 0.44, 1],  # #f87171
}


class StyledButton(Button):
    """Custom styled button with gold theme"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['gold']
        self.color = COLORS['bg_dark']
        self.bold = True
        self.font_size = '18sp'
        

class StyledSpinner(Spinner):
    """Custom styled dropdown"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['bg_secondary']
        self.color = COLORS['text_primary']
        self.option_cls.background_color = COLORS['bg_secondary']
        self.option_cls.color = COLORS['text_primary']
        

class NumberInput(BoxLayout):
    """Number input with +/- buttons"""
    value = NumericProperty(1)
    min_value = NumericProperty(1)
    max_value = NumericProperty(286)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '50dp'
        self.spacing = '10dp'
        
        # Decrease button
        self.decrease_btn = Button(
            text='−',
            size_hint_x=None,
            width='50dp',
            background_normal='',
            background_color=COLORS['bg_secondary'],
            color=COLORS['gold'],
            font_size='24sp',
            bold=True
        )
        self.decrease_btn.bind(on_press=self.decrease)
        self.add_widget(self.decrease_btn)
        
        # Text input
        self.text_input = TextInput(
            text=str(self.value),
            multiline=False,
            input_filter='int',
            halign='center',
            font_size='18sp',
            background_color=COLORS['bg_secondary'],
            foreground_color=COLORS['text_primary'],
            cursor_color=COLORS['gold']
        )
        self.text_input.bind(text=self.on_text_change)
        self.add_widget(self.text_input)
        
        # Increase button
        self.increase_btn = Button(
            text='+',
            size_hint_x=None,
            width='50dp',
            background_normal='',
            background_color=COLORS['bg_secondary'],
            color=COLORS['gold'],
            font_size='24sp',
            bold=True
        )
        self.increase_btn.bind(on_press=self.increase)
        self.add_widget(self.increase_btn)
    
    def decrease(self, instance):
        if self.value > self.min_value:
            self.value -= 1
            self.text_input.text = str(self.value)
    
    def increase(self, instance):
        if self.value < self.max_value:
            self.value += 1
            self.text_input.text = str(self.value)
    
    def on_text_change(self, instance, value):
        try:
            val = int(value) if value else self.min_value
            val = max(self.min_value, min(val, self.max_value))
            self.value = val
            self.text_input.text = str(val)
        except:
            pass
    
    def get_value(self):
        return self.value
    
    def set_max(self, max_val):
        self.max_value = max_val
        if self.value > max_val:
            self.value = max_val
            self.text_input.text = str(self.value)


class LogConsole(ScrollView):
    """Scrollable log console"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = '150dp'
        
        self.log_label = Label(
            text='',
            size_hint_y=None,
            halign='left',
            valign='top',
            color=COLORS['text_secondary'],
            font_size='12sp',
            font_name='monospace',
            markup=True
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.add_widget(self.log_label)
        
    def add_log(self, message, log_type='info'):
        color = {
            'info': 'd4af37',
            'success': '4ade80',
            'error': 'f87171'
        }.get(log_type, 'd4af37')
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_line = f"[color={color}][{timestamp}] {message}[/color]\n"
        
        current_text = self.log_label.text
        self.log_label.text = current_text + log_line
        
        # Auto-scroll to bottom
        self.scroll_y = 0


class MainLayout(BoxLayout):
    """Main application layout"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = '20dp'
        self.spacing = '15dp'
        
        # Set window background
        Window.clearcolor = COLORS['bg_dark']
        
        # Initialize generator
        self.generator = None
        self.generation_thread = None
        
        # Build UI
        self.build_header()
        self.build_form()
        self.build_progress_section()
        self.build_log_console()
        self.build_footer()
        
        # Bind surah change to update ayah limits
        self.surah_spinner.bind(text=self.on_surah_change)
        
        # Setup periodic progress check
        Clock.schedule_interval(self.check_progress, 0.1)
        
    def build_header(self):
        """Build app header with logo"""
        header = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp')
        
        # Logo/Title
        title = Label(
            text='أداة الريلز الدينية',
            font_size='32sp',
            bold=True,
            color=COLORS['gold'],
            size_hint_y=None,
            height='50dp'
        )
        header.add_widget(title)
        
        subtitle = Label(
            text='QURAN REELS GENERATOR',
            font_size='14sp',
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height='30dp'
        )
        header.add_widget(subtitle)
        
        self.add_widget(header)
        
    def build_form(self):
        """Build main form with inputs"""
        form_card = BoxLayout(orientation='vertical', spacing='15dp')
        
        # Card title
        card_title = Label(
            text='✨ عمل الريلز قرآنية ✨',
            font_size='24sp',
            bold=True,
            color=COLORS['gold'],
            size_hint_y=None,
            height='40dp'
        )
        form_card.add_widget(card_title)
        
        # Reciter selection
        form_card.add_widget(Label(
            text='القارئ',
            color=COLORS['text_primary'],
            size_hint_y=None,
            height='30dp',
            halign='right'
        ))
        
        reciters = list(RECITERS_MAP.keys())
        self.reciter_spinner = StyledSpinner(
            text=reciters[0],
            values=reciters,
            size_hint_y=None,
            height='50dp'
        )
        form_card.add_widget(self.reciter_spinner)
        
        # Surah selection
        form_card.add_widget(Label(
            text='السورة',
            color=COLORS['text_primary'],
            size_hint_y=None,
            height='30dp',
            halign='right'
        ))
        
        surahs = [f"{i+1}. {name}" for i, name in enumerate(SURAH_NAMES)]
        self.surah_spinner = StyledSpinner(
            text=surahs[0],
            values=surahs,
            size_hint_y=None,
            height='50dp'
        )
        form_card.add_widget(self.surah_spinner)
        
        # Start Ayah
        form_card.add_widget(Label(
            text='آية البداية',
            color=COLORS['text_primary'],
            size_hint_y=None,
            height='30dp',
            halign='right'
        ))
        self.start_ayah_input = NumberInput()
        form_card.add_widget(self.start_ayah_input)
        
        # End Ayah
        form_card.add_widget(Label(
            text='آية النهاية',
            color=COLORS['text_primary'],
            size_hint_y=None,
            height='30dp',
            halign='right'
        ))
        self.end_ayah_input = NumberInput()
        self.end_ayah_input.value = 7  # Default to 7 verses
        self.end_ayah_input.text_input.text = '7'
        form_card.add_widget(self.end_ayah_input)
        
        # Generate button
        self.generate_btn = StyledButton(
            text='إنشاء الفيديو',
            size_hint_y=None,
            height='60dp'
        )
        self.generate_btn.bind(on_press=self.on_generate)
        form_card.add_widget(self.generate_btn)
        
        # Cancel button (initially disabled)
        self.cancel_btn = Button(
            text='إلغاء',
            size_hint_y=None,
            height='50dp',
            background_normal='',
            background_color=COLORS['error'],
            color=[1, 1, 1, 1],
            disabled=True,
            opacity=0
        )
        self.cancel_btn.bind(on_press=self.on_cancel)
        form_card.add_widget(self.cancel_btn)
        
        self.add_widget(form_card)
        
    def build_progress_section(self):
        """Build progress bar and status"""
        self.progress_section = BoxLayout(
            orientation='vertical',
            spacing='10dp',
            size_hint_y=None,
            height='100dp',
            opacity=0
        )
        
        # Progress header
        progress_header = BoxLayout(size_hint_y=None, height='30dp')
        self.progress_title = Label(
            text='جاري إنشاء الفيديو...',
            color=COLORS['text_secondary'],
            size_hint_x=0.7
        )
        self.progress_percent = Label(
            text='0%',
            color=COLORS['gold'],
            bold=True,
            size_hint_x=0.3
        )
        progress_header.add_widget(self.progress_title)
        progress_header.add_widget(self.progress_percent)
        self.progress_section.add_widget(progress_header)
        
        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height='20dp'
        )
        self.progress_section.add_widget(self.progress_bar)
        
        # Status label
        self.status_label = Label(
            text='جاري التحضير...',
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height='40dp'
        )
        self.progress_section.add_widget(self.status_label)
        
        self.add_widget(self.progress_section)
        
    def build_log_console(self):
        """Build log console"""
        self.log_console = LogConsole()
        self.add_widget(self.log_console)
        
    def build_footer(self):
        """Build footer"""
        footer = Label(
            text='© 2024 جميع الحقوق محفوظة',
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height='40dp',
            font_size='12sp'
        )
        self.add_widget(footer)
        
    def on_surah_change(self, spinner, text):
        """Update ayah limits when surah changes"""
        try:
            surah_num = int(text.split('.')[0])
            max_ayah = VERSE_COUNTS[surah_num]
            
            self.start_ayah_input.set_max(max_ayah)
            self.end_ayah_input.set_max(max_ayah)
            
            # Set default end to min(start+6, max)
            default_end = min(7, max_ayah)
            self.end_ayah_input.value = default_end
            self.end_ayah_input.text_input.text = str(default_end)
            
        except Exception as e:
            print(f"Error updating surah: {e}")
            
    def on_generate(self, instance):
        """Start video generation"""
        if self.generator and self.generator.is_running:
            return
        
        # Get values
        reciter_name = self.reciter_spinner.text
        reciter_id = RECITERS_MAP[reciter_name]
        
        surah_text = self.surah_spinner.text
        surah = int(surah_text.split('.')[0])
        
        start_ayah = self.start_ayah_input.get_value()
        end_ayah = self.end_ayah_input.get_value()
        
        # Validate
        if end_ayah < start_ayah:
            self.show_error('آية النهاية يجب أن تكون أكبر من آية البداية')
            return
        
        max_ayah = VERSE_COUNTS[surah]
        if end_ayah > max_ayah:
            self.show_error(f'السورة {surah_text} تحتوي على {max_ayah} آيات فقط')
            return
        
        # Update UI
        self.generate_btn.disabled = True
        self.generate_btn.opacity = 0.5
        self.cancel_btn.disabled = False
        self.cancel_btn.opacity = 1
        self.progress_section.opacity = 1
        self.progress_bar.value = 0
        self.progress_percent.text = '0%'
        self.log_console.log_label.text = ''
        
        # Create generator
        self.generator = VideoGenerator(
            progress_callback=self.on_progress_update,
            log_callback=self.on_log_message
        )
        
        # Start generation in thread
        self.generation_thread = threading.Thread(
            target=self.run_generation,
            args=(reciter_id, surah, start_ayah, end_ayah)
        )
        self.generation_thread.daemon = True
        self.generation_thread.start()
        
    def run_generation(self, reciter_id, surah, start_ayah, end_ayah):
        """Run video generation in background thread"""
        success, output_path, error = self.generator.generate_video(
            reciter_id, surah, start_ayah, end_ayah
        )
        
        # Schedule UI update on main thread
        Clock.schedule_once(
            lambda dt: self.on_generation_complete(success, output_path, error),
            0
        )
        
    def on_progress_update(self, percent, status):
        """Callback for progress updates"""
        Clock.schedule_once(
            lambda dt: self.update_progress_ui(percent, status),
            0
        )
        
    def update_progress_ui(self, percent, status):
        """Update progress UI on main thread"""
        self.progress_bar.value = percent
        self.progress_percent.text = f'{percent}%'
        self.status_label.text = status
        
    def on_log_message(self, message):
        """Callback for log messages"""
        Clock.schedule_once(
            lambda dt: self.add_log_message(message),
            0
        )
        
    def add_log_message(self, message):
        """Add log message to console"""
        log_type = 'success' if 'Done' in message or 'تم بنجاح' in message else \
                   'error' if 'ERROR' in message or 'خطأ' in message else 'info'
        self.log_console.add_log(message, log_type)
        
    def on_generation_complete(self, success, output_path, error):
        """Handle generation completion"""
        # Reset UI
        self.generate_btn.disabled = False
        self.generate_btn.opacity = 1
        self.cancel_btn.disabled = True
        self.cancel_btn.opacity = 0
        
        if success:
            self.status_label.text = 'تم بنجاح! ✨'
            self.status_label.color = COLORS['success']
            self.show_success_popup(output_path)
        else:
            self.status_label.text = f'خطأ: {error}'
            self.status_label.color = COLORS['error']
            if error != "Cancelled by user":
                self.show_error(f'حدث خطأ: {error}')
        
    def on_cancel(self, instance):
        """Cancel video generation"""
        if self.generator:
            self.generator.stop()
            self.add_log_message('جاري إلغاء العملية...')
            
    def check_progress(self, dt):
        """Periodic progress check (if needed)"""
        pass
        
    def show_success_popup(self, output_path):
        """Show success popup with output location"""
        content = BoxLayout(orientation='vertical', spacing='10dp', padding='20dp')
        
        content.add_widget(Label(
            text='✓ تم بنجاح!',
            font_size='24sp',
            bold=True,
            color=COLORS['success']
        ))
        
        content.add_widget(Label(
            text=f'تم حفظ الفيديو في:\n{output_path}',
            color=COLORS['text_secondary'],
            halign='center'
        ))
        
        close_btn = Button(
            text='إغلاق',
            size_hint_y=None,
            height='50dp',
            background_normal='',
            background_color=COLORS['gold'],
            color=COLORS['bg_dark']
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False,
            background_color=COLORS['bg_secondary']
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
        
    def show_error(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', spacing='10dp', padding='20dp')
        
        content.add_widget(Label(
            text='⚠ خطأ',
            font_size='20sp',
            bold=True,
            color=COLORS['error']
        ))
        
        content.add_widget(Label(
            text=message,
            color=COLORS['text_secondary'],
            halign='center'
        ))
        
        close_btn = Button(
            text='إغلاق',
            size_hint_y=None,
            height='50dp',
            background_normal='',
            background_color=COLORS['error'],
            color=[1, 1, 1, 1]
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False,
            background_color=COLORS['bg_secondary']
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()


class QuranReelsApp(App):
    """Main Kivy Application"""
    
    def build(self):
        self.title = 'Quran Reels Generator'
        return MainLayout()


if __name__ == '__main__':
    QuranReelsApp().run()
