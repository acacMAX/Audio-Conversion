#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频转换工具 - 通用音频格式转换器
支持所有音频格式之间的互相转换
支持批量转换，可选择是否删除原文件
"""

import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import queue
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False


class AudioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("音频转换工具 - 通用音频格式转换器")
        self.root.geometry("750x700")
        self.root.resizable(True, True)
        
        # 设置图标和样式
        self.setup_styles()
        
        # 文件列表
        self.file_list = []
        self.conversion_queue = queue.Queue()
        self.is_converting = False
        
        # 设置输出目录为"音乐"文件夹
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "音乐")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 启用拖拽功能
        if HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # 创建界面
        self.create_widgets()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 现代化配色方案
        bg_color = '#2d3436'
        card_bg = '#363d40'
        accent_color = '#0984e3'
        accent_hover = '#74b9ff'
        text_primary = '#dfe6e9'
        text_secondary = '#b2bec3'
        success_color = '#00b894'
        warning_color = '#fdcb6e'
        danger_color = '#d63031'
        
        # 背景颜色
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color, foreground=text_primary)
        style.configure('TLabelframe.Label', background=bg_color, foreground=text_primary, font=('Microsoft YaHei UI', 10, 'bold'))
        
        # 标签样式
        style.configure('TLabel', background=bg_color, foreground=text_primary, font=('Microsoft YaHei UI', 10))
        style.configure('Header.TLabel', font=('Microsoft YaHei UI', 18, 'bold'), background=bg_color, foreground=text_primary)
        style.configure('Status.TLabel', background=bg_color, foreground=text_secondary, font=('Microsoft YaHei UI', 9))
        
        # 按钮样式
        style.configure('TButton', font=('Microsoft YaHei UI', 10), padding=8, background=card_bg, foreground=text_primary)
        style.map('TButton', background=[('active', accent_color)], foreground=[('active', 'white')])
        
        # Entry 样式
        style.configure('TEntry', fieldbackground=card_bg, foreground=text_primary, insertcolor=text_primary, padding=8)
        
        # Combobox 样式
        style.configure('TCombobox', fieldbackground=card_bg, foreground=text_primary, insertcolor=text_primary, padding=6)
        style.map('TCombobox', selectbackground=[('focus', accent_color)], selectforeground=[('focus', 'white')])
        
        # Progressbar 样式
        style.configure('Horizontal.TProgressbar', troughcolor=card_bg, background=accent_color, thickness=20)
        
        # Checkbutton 样式
        style.configure('TCheckbutton', background=bg_color, foreground=text_primary, font=('Microsoft YaHei UI', 10))
        
        # ScrolledText 样式
        style.configure('TScrolledText', background=card_bg, foreground=text_secondary, font=('Consolas', 9))
        
        # 保存颜色常量
        self.colors = {
            'bg': bg_color,
            'card_bg': card_bg,
            'accent': accent_color,
            'text_primary': text_primary,
            'text_secondary': text_secondary,
            'success': success_color,
            'warning': warning_color,
            'danger': danger_color
        }
        
        self.root.configure(bg=bg_color)
        
    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题区域
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame, 
            text="🎵 音频转换工具", 
            style='Header.TLabel',
            font=('Microsoft YaHei UI', 20, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(
            title_frame,
            text="通用音频格式转换器",
            style='Status.TLabel',
            font=('Microsoft YaHei UI', 9)
        )
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="📁 选择文件", padding="12")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        file_frame.columnconfigure(0, weight=1)
        
        # 文件路径显示
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(
            file_frame, 
            textvariable=self.file_path_var,
            font=('Microsoft YaHei UI', 9)
        )
        file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 8))
        
        # 选择文件按钮
        select_file_btn = ttk.Button(
            file_frame, 
            text="📄 选择文件", 
            command=self.select_files,
            width=12
        )
        select_file_btn.grid(row=0, column=1, padx=(0, 6))
        
        # 选择文件夹按钮
        select_folder_btn = ttk.Button(
            file_frame, 
            text="📂 选择文件夹", 
            command=self.select_folder,
            width=12
        )
        select_folder_btn.grid(row=0, column=2)
        
        # 选项区域
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ 转换选项", padding="12")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        
        # 输出格式选择
        format_label = ttk.Label(options_frame, text="输出格式:")
        format_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        self.output_format_var = tk.StringVar(value="mp3")
        format_combo = ttk.Combobox(
            options_frame,
            textvariable=self.output_format_var,
            values=["mp3", "flac", "wav", "ogg", "m4a", "aac", "wma"],
            state="readonly",
            width=12
        )
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=(8, 25), pady=(0, 8))
        format_combo.bind("<<ComboboxSelected>>", self.on_format_change)
        
        # 删除原文件选项
        self.delete_original_var = tk.BooleanVar(value=False)
        delete_check = ttk.Checkbutton(
            options_frame,
            text="转换完成后删除原文件",
            variable=self.delete_original_var
        )
        delete_check.grid(row=0, column=2, sticky=tk.W, pady=(0, 8))
        
        # 质量选项
        self.quality_label = ttk.Label(options_frame, text="质量:")
        self.quality_label.grid(row=1, column=0, sticky=tk.W)
        
        self.quality_var = tk.StringVar(value="高质量 (192 kbps)")
        self.quality_combo = ttk.Combobox(
            options_frame,
            textvariable=self.quality_var,
            values=["高质量 (192 kbps)", "中等质量 (128 kbps)", "低质量 (64 kbps)"],
            state="readonly",
            width=20
        )
        self.quality_combo.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=(8, 0))
        
        # 进度区域
        progress_frame = ttk.LabelFrame(main_frame, text="📊 转换进度", padding="12")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 12))
        progress_frame.columnconfigure(0, weight=1)
        
        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # 状态标签
        self.status_var = tk.StringVar(value="等待选择文件...")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var, style='Status.TLabel')
        status_label.grid(row=1, column=0, sticky=tk.W)
        
        # 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="📝 转换日志", padding="12")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 12))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=('Consolas', 9),
            wrap=tk.WORD,
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            insertbackground=self.colors['text_primary'],
            borderwidth=0,
            highlightthickness=0
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置日志文本颜色
        self.log_text.tag_config('success', foreground=self.colors['success'])
        self.log_text.tag_config('error', foreground=self.colors['danger'])
        self.log_text.tag_config('info', foreground=self.colors['text_primary'])
        self.log_text.tag_config('warning', foreground=self.colors['warning'])
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        # 开始转换按钮
        self.start_btn = ttk.Button(
            button_frame,
            text="▶️ 开始转换",
            command=self.start_conversion,
            state=tk.DISABLED,
            width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # 停止转换按钮
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹️ 停止转换",
            command=self.stop_conversion,
            state=tk.DISABLED,
            width=15
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # 清空按钮
        self.clear_btn = ttk.Button(
            button_frame,
            text="🗑️ 清空列表",
            command=self.clear_files,
            width=15
        )
        self.clear_btn.pack(side=tk.LEFT)
        
    def log(self, message, tag=None):
        """添加日志"""
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.update()
        
    def on_format_change(self, event=None):
        """格式变化时更新质量选项"""
        output_format = self.output_format_var.get()
        
        # 根据格式更新质量选项
        if output_format in ['mp3', 'm4a', 'aac', 'wma']:
            # 有损格式，显示比特率选项
            self.quality_label.config(state=tk.NORMAL)
            self.quality_combo.config(state="readonly")
            if output_format == 'mp3':
                self.quality_var.set("高质量 (192 kbps)")
                self.quality_combo['values'] = ["高质量 (192 kbps)", "中等质量 (128 kbps)", "低质量 (64 kbps)"]
            elif output_format == 'm4a':
                self.quality_var.set("高质量 (256 kbps)")
                self.quality_combo['values'] = ["高质量 (256 kbps)", "中等质量 (192 kbps)", "低质量 (128 kbps)"]
            elif output_format == 'aac':
                self.quality_var.set("高质量 (192 kbps)")
                self.quality_combo['values'] = ["高质量 (192 kbps)", "中等质量 (128 kbps)", "低质量 (64 kbps)"]
            elif output_format == 'wma':
                self.quality_var.set("高质量 (192 kbps)")
                self.quality_combo['values'] = ["高质量 (192 kbps)", "中等质量 (128 kbps)", "低质量 (64 kbps)"]
        elif output_format in ['flac', 'wav']:
            # 无损格式，显示采样率选项
            self.quality_label.config(state=tk.NORMAL)
            self.quality_combo.config(state="readonly")
            self.quality_var.set("无损 (原始音质)")
            self.quality_combo['values'] = ["无损 (原始音质)", "高质量 (48kHz)", "标准质量 (44.1kHz)"]
        elif output_format == 'ogg':
            # OGG 格式
            self.quality_label.config(state=tk.NORMAL)
            self.quality_combo.config(state="readonly")
            self.quality_var.set("高质量 (256 kbps)")
            self.quality_combo['values'] = ["高质量 (256 kbps)", "中等质量 (192 kbps)", "低质量 (128 kbps)"]
    
    @staticmethod
    def get_supported_extensions():
        """获取支持的音频格式扩展名"""
        return {'.flac', '.wav', '.ogg', '.m4a', '.aac', '.wma', '.mp3', '.opus', '.aiff', '.au'}
        
    def on_drop(self, event):
        """处理拖拽的文件"""
        # 处理 Windows 路径格式（大括号）
        files_str = event.data
        if files_str.startswith('{') and files_str.endswith('}'):
            files_str = files_str[1:-1]
        
        # 分割文件路径
        if os.name == 'nt':  # Windows
            files = files_str.split('}')
        else:  # Unix/Linux
            files = files_str.split()
        
        # 过滤音频文件
        audio_extensions = self.get_supported_extensions()
        audio_files = []
        
        for file_path in files:
            file_path = file_path.strip()
            if not file_path:
                continue
            # 处理 Windows 路径（可能包含空格）
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    if Path(file_path).suffix.lower() in audio_extensions:
                        audio_files.append(file_path)
                elif os.path.isdir(file_path):
                    # 如果是文件夹，递归查找音频文件
                    for root, dirs, filenames in os.walk(file_path):
                        for filename in filenames:
                            if Path(filename).suffix.lower() in audio_extensions:
                                audio_files.append(os.path.join(root, filename))
        
        if audio_files:
            self.file_list.extend(audio_files)
            self.file_path_var.set(f"已选择 {len(self.file_list)} 个文件")
            self.start_btn.config(state=tk.NORMAL)
            self.log(f"✓ 拖拽添加 {len(audio_files)} 个音频文件", 'success')
        
    def select_files(self):
        """选择文件"""
        files = filedialog.askopenfilenames(
            title="选择音频文件",
            filetypes=[
                ("所有音频文件", "*.mp3 *.flac *.wav *.ogg *.m4a *.aac *.wma *.opus *.aiff *.au"),
                ("MP3 文件", "*.mp3"),
                ("FLAC 文件", "*.flac"),
                ("WAV 文件", "*.wav"),
                ("OGG 文件", "*.ogg"),
                ("M4A 文件", "*.m4a"),
                ("AAC 文件", "*.aac"),
                ("WMA 文件", "*.wma"),
                ("OPUS 文件", "*.opus"),
                ("AIFF 文件", "*.aiff"),
                ("所有文件", "*.*")
            ]
        )
        
        if files:
            self.file_list.extend(files)
            self.file_path_var.set(f"已选择 {len(self.file_list)} 个文件")
            self.start_btn.config(state=tk.NORMAL)
            self.log(f"✓ 添加 {len(files)} 个文件到转换列表", 'success')
            
    def select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title="选择文件夹")
        
        if folder:
            audio_extensions = self.get_supported_extensions()
            files = []
            
            for root, dirs, filenames in os.walk(folder):
                for filename in filenames:
                    if Path(filename).suffix.lower() in audio_extensions:
                        files.append(os.path.join(root, filename))
            
            if files:
                self.file_list.extend(files)
                self.file_path_var.set(f"已选择 {len(self.file_list)} 个文件")
                self.start_btn.config(state=tk.NORMAL)
                self.log(f"✓ 从文件夹添加 {len(files)} 个音频文件", 'success')
            else:
                messagebox.showwarning("警告", "所选文件夹中没有找到音频文件")
                
    def clear_files(self):
        """清空文件列表"""
        self.file_list.clear()
        self.file_path_var.set("")
        self.start_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("等待选择文件...")
        self.log("🗑️ 已清空文件列表", 'info')
        
    def get_quality_bitrate(self):
        """获取质量对应的比特率"""
        quality = self.quality_var.get()
        if "高质量" in quality:
            return "192"
        elif "中等质量" in quality:
            return "128"
        else:
            return "64"
            
    def convert_file(self, input_file, output_file):
        """转换单个文件"""
        try:
            # 生成输出文件路径（保存到音乐文件夹）
            input_path = Path(input_file)
            output_format = self.output_format_var.get()
            output_file = os.path.join(self.output_dir, input_path.stem + '.' + output_format)
            
            # 构建转换命令
            cmd = ['ffmpeg', '-y', '-i', input_file, '-vn']  # -vn: 不处理视频流
            
            # 记录命令用于调试
            self.debug_cmd = ' '.join(f'"{arg}"' if ' ' in str(arg) else str(arg) for arg in cmd)
            
            # 根据输出格式设置编码器
            quality = self.quality_var.get()
            
            if output_format == 'mp3':
                cmd.extend(['-codec:a', 'libmp3lame'])
                if '高质量' in quality:
                    cmd.extend(['-b:a', '192k'])
                elif '中等质量' in quality:
                    cmd.extend(['-b:a', '128k'])
                else:
                    cmd.extend(['-b:a', '64k'])
            elif output_format == 'flac':
                cmd.extend(['-codec:a', 'flac'])
                if '无损' not in quality:
                    if '高质量' in quality:
                        cmd.extend(['-ar', '48000'])
                    else:
                        cmd.extend(['-ar', '44100'])
            elif output_format == 'wav':
                cmd.extend(['-codec:a', 'pcm_s16le'])
                if '无损' not in quality:
                    if '高质量' in quality:
                        cmd.extend(['-ar', '48000'])
                    else:
                        cmd.extend(['-ar', '44100'])
            elif output_format == 'ogg':
                cmd.extend(['-codec:a', 'libvorbis'])
                if '高质量' in quality:
                    cmd.extend(['-b:a', '256k'])
                elif '中等质量' in quality:
                    cmd.extend(['-b:a', '192k'])
                else:
                    cmd.extend(['-b:a', '128k'])
            elif output_format == 'm4a':
                # m4a 使用 mov 容器格式
                cmd.extend(['-vn'])  # 不处理视频流
                cmd.extend(['-f', 'mov'])
                cmd.extend(['-codec:a', 'aac'])
                if '高质量' in quality:
                    cmd.extend(['-b:a', '256k'])
                elif '中等质量' in quality:
                    cmd.extend(['-b:a', '192k'])
                else:
                    cmd.extend(['-b:a', '128k'])
            elif output_format == 'aac':
                cmd.extend(['-codec:a', 'aac'])
                if '高质量' in quality:
                    cmd.extend(['-b:a', '192k'])
                elif '中等质量' in quality:
                    cmd.extend(['-b:a', '128k'])
                else:
                    cmd.extend(['-b:a', '64k'])
            elif output_format == 'wma':
                cmd.extend(['-codec:a', 'wmav2'])
                if '高质量' in quality:
                    cmd.extend(['-b:a', '192k'])
                elif '中等质量' in quality:
                    cmd.extend(['-b:a', '128k'])
                else:
                    cmd.extend(['-b:a', '64k'])
            
            cmd.append(output_file)
            
            # 调试：显示完整命令
            import shlex
            cmd_str = ' '.join(shlex.quote(str(arg)) for arg in cmd)
            # 在实际执行时，这个日志会被 conversion_worker 中的日志调用覆盖
            # 所以我们只在这里记录命令，不直接输出
            
            # 设置环境变量以包含 ffmpeg 路径
            env = os.environ.copy()
            system_path = os.environ.get('PATH', '')
            user_path = os.environ.get('USERPROFILE', '')
            
            # 添加常见的 ffmpeg 安装路径
            ffmpeg_paths = [
                os.path.join(user_path, 'scoop', 'shims'),
                os.path.join(user_path, 'AppData', 'Local', 'Microsoft', 'WinGet', 'Packages'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'ffmpeg'),
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'ffmpeg', 'bin'),
            ]
            
            for path in ffmpeg_paths:
                if os.path.exists(path) and path not in system_path:
                    system_path = path + os.pathsep + system_path
            
            env['PATH'] = system_path
            
            # 在 Windows 上处理路径中的空格和特殊字符
            if os.name == 'nt':
                # Windows: 确保路径被正确处理
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    timeout=300,  # 5分钟超时
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    timeout=300  # 5分钟超时
                )
            
            if result.returncode == 0:
                return True, output_file  # 返回输出文件路径
            else:
                # 将 stderr 错误信息解码并返回
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                # 提取关键错误信息
                if 'Invalid data' in error_msg:
                    return False, "输入文件数据无效或损坏"
                elif 'Permission denied' in error_msg:
                    return False, "权限被拒绝，无法写入文件"
                elif 'No space left' in error_msg:
                    return False, "磁盘空间不足"
                elif 'Error' in error_msg:
                    # 查找包含 Error 的行
                    for line in error_msg.split('\n'):
                        if 'Error' in line and 'ffmpeg' not in line.lower():
                            # 附加命令信息用于调试
                            cmd_info = getattr(self, 'debug_cmd', '')
                            return False, f"FFmpeg错误: {line.strip()}"
                    # 如果没找到具体的 Error 行，返回最后一行
                    return False, f"FFmpeg错误: {error_msg.split('\n')[-1].strip()}"
                else:
                    # 返回最后一行的错误信息
                    last_line = [l for l in error_msg.split('\n') if l.strip()][-1] if error_msg else "未知错误"
                    return False, f"转换失败: {last_line}"
                
        except subprocess.TimeoutExpired:
            return False, "转换超时"
        except Exception as e:
            return False, f"错误: {str(e)}"
            
    def start_conversion(self):
        """开始转换"""
        if not self.file_list:
            messagebox.showwarning("警告", "请先选择要转换的文件")
            return
            
        self.is_converting = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.DISABLED)
        
        # 在新线程中执行转换
        thread = threading.Thread(target=self.conversion_worker, daemon=True)
        thread.start()
        
    def stop_conversion(self):
        """停止转换"""
        self.is_converting = False
        self.log("⏸️ 正在停止转换...", 'warning')
        self.status_var.set("已停止")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.NORMAL)
        
    def conversion_worker(self):
        """转换工作线程"""
        total_files = len(self.file_list)
        converted_files = 0
        failed_files = []
        delete_original = self.delete_original_var.get()
        output_format = self.output_format_var.get()
        
        self.log("="*60, 'info')
        self.log(f"🚀 开始转换 {total_files} 个文件...", 'info')
        self.log(f"📝 输出格式: {output_format.upper()}", 'info')
        self.log(f"📁 输出目录: {self.output_dir}", 'info')
        self.log("="*60, 'info')
        self.status_var.set(f"准备转换 {total_files} 个文件...")
        
        # 检查输出目录是否可写
        if not os.access(self.output_dir, os.W_OK):
            self.log(f"❌ 错误: 输出目录不可写 - {self.output_dir}", 'error')
            messagebox.showerror("错误", f"无法写入输出目录:\n{self.output_dir}\n\n请检查目录权限。")
            self.is_converting = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.clear_btn.config(state=tk.NORMAL)
            return
        
        for i, input_file in enumerate(self.file_list):
            if not self.is_converting:
                self.log("⚠️ 转换已取消", 'warning')
                break
                
            try:
                # 显示当前转换的文件
                input_path = Path(input_file)
                file_name = input_path.name
                self.log(f"\n[{i+1}/{total_files}] 🎵 {file_name} → {output_format.upper()}", 'info')
                self.status_var.set(f"正在转换: {file_name}")
                
                # 执行转换
                success, message = self.convert_file(input_file, "")
                
                if success:
                    converted_files += 1
                    output_path = Path(message)
                    self.log(f"  ✅ 转换成功", 'success')
                    self.log(f"  💾 保存位置: {output_path}", 'info')
                    
                    # 删除原文件
                    if delete_original:
                        try:
                            os.remove(input_file)
                            self.log(f"  🗑️ 已删除原文件", 'warning')
                        except Exception as e:
                            self.log(f"  ❌ 删除原文件失败: {str(e)}", 'error')
                else:
                    failed_files.append((file_name, message))
                    self.log(f"  ❌ 转换失败: {message}", 'error')
                    
                # 更新进度
                progress = ((i + 1) / total_files) * 100
                self.progress_var.set(progress)
                self.status_var.set(f"进度: {i+1}/{total_files} ({progress:.1f}%)")
                
            except Exception as e:
                failed_files.append((input_file, str(e)))
                self.log(f"  ❌ 处理文件时出错: {str(e)}", 'error')
                
        # 转换完成
        self.is_converting = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.NORMAL)
        
        # 显示结果
        self.log("\n" + "="*60, 'info')
        self.log(f"🎉 转换完成！", 'info')
        self.log(f"📊 成功: {converted_files} 个  ❌ 失败: {len(failed_files)} 个", 'info')
        self.log("="*60, 'info')
        
        if failed_files:
            self.log("\n❌ 失败的文件:", 'error')
            for file_name, error in failed_files:
                self.log(f"  • {file_name}: {error}", 'error')
                
        self.status_var.set(f"✅ 转换完成: {converted_files}/{total_files} 成功")
        
        # 询问是否清空列表
        if converted_files > 0:
            response = messagebox.askyesno(
                "转换完成",
                f"转换已完成！\n成功: {converted_files} 个\n失败: {len(failed_files)} 个\n\n是否清空文件列表？"
            )
            if response:
                self.root.after(0, self.clear_files)


def main():
    """主函数"""
    # 如果支持拖拽，使用 TkinterDnD.Tk
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    app = AudioConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()