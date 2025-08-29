import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image
from PIL import ImageOps
import glob

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图像处理工具")
        self.root.geometry("500x500")  # 增加了高度以适应新控件
        self.root.resizable(False, False)
        
        # 默认设置
        self.target_size = tk.IntVar(value=1024)
        self.channel_map = {
            'R': tk.StringVar(value='R'),
            'G': tk.StringVar(value='G'),
            'B': tk.StringVar(value='B'),
            'A': tk.StringVar(value='A')
        }
        
        # 添加反转选项
        self.invert_options = {
            'R': tk.BooleanVar(value=False),
            'G': tk.BooleanVar(value=False),
            'B': tk.BooleanVar(value=False),
            'A': tk.BooleanVar(value=False)
        }
        
        # 添加覆盖源文件选项和输出格式
        self.overwrite_source = tk.BooleanVar(value=False)
        self.output_format = tk.StringVar(value='TGA')
        self.output_formats = ['PNG', 'TGA', 'JPG']

        # 创建UI
        self.create_widgets()
        
        # 文件列表
        self.files_to_process = []
    
    def create_widgets(self):
        # 目标尺寸框架
        size_frame = ttk.LabelFrame(self.root, text="目标尺寸")
        size_frame.pack(fill='x', padx=10, pady=5)
        
        sizes = [1024, 512, 256]
        for size in sizes:
            ttk.Radiobutton(
                size_frame, text=str(size),
                variable=self.target_size, 
                value=size
            ).pack(side='left', padx=10, pady=5)
        
        # 通道映射框架
        channel_frame = ttk.LabelFrame(self.root, text="通道映射")
        channel_frame.pack(fill='x', padx=10, pady=5)
        
        channels = ['R', 'G', 'B', 'A']
        for channel in channels:
            row = ttk.Frame(channel_frame)
            row.pack(fill='x', padx=5, pady=2)
            
            ttk.Label(row, text=f"{channel} 通道来源:").pack(side='left', padx=(10, 5))
            cb = ttk.Combobox(
                row, 
                values=channels, 
                textvariable=self.channel_map[channel],
                width=5,
                state="readonly"
            )
            cb.pack(side='left')

            # 通道反转
            ttk.Checkbutton(
                row,
                text="反转",
                variable=self.invert_options[channel]
            ).pack(side='left', padx=(5, 0))
        
        # 输出选项框架
        output_frame = ttk.LabelFrame(self.root, text="输出选项")
        output_frame.pack(fill='x', padx=10, pady=5)
        
        # 覆盖源文件选项
        overwrite_check = ttk.Checkbutton(
            output_frame,
            text="覆盖源文件",
            variable=self.overwrite_source,
            command=self.toggle_output_format_state
        )
        overwrite_check.pack(side='left', padx=10, pady=5)
        
        # 输出格式下拉菜单
        format_row = ttk.Frame(output_frame)
        format_row.pack(side='left', padx=5, pady=5)
        
        ttk.Label(format_row, text="输出格式:").pack(side='left', padx=(0, 5))
        self.format_combobox = ttk.Combobox(
            format_row,
            textvariable=self.output_format,
            values=self.output_formats,
            state="readonly",
            width=5
        )
        self.format_combobox.pack(side='left')
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.root, text="文件处理")
        file_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 文件列表框
        self.file_listbox = tk.Listbox(
            file_frame, 
            height=6,
            selectmode=tk.EXTENDED
        )
        self.file_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            button_frame, 
            text="添加文件", 
            command=self.add_files
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame, 
            text="清除列表", 
            command=self.clear_list
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame, 
            text="开始处理", 
            command=self.process_images
        ).pack(side='right', padx=5)
    
    def toggle_output_format_state(self):
        """根据覆盖源文件选项切换输出格式下拉菜单的状态"""
        if self.overwrite_source.get():
            self.format_combobox.config(state='disabled')
        else:
            self.format_combobox.config(state='readonly')
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="选择图像文件",
            filetypes=(
                ("图像文件", "*.png;*.jpg;*.jpeg;*.bmp;*.tga"),
                ("所有文件", "*.*")
            )
        )
        
        if files:
            self.files_to_process.extend(files)
            self.update_file_listbox()
    
    def clear_list(self):
        self.files_to_process = []
        self.file_listbox.delete(0, tk.END)
    
    def update_file_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.files_to_process:
            self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def resize_image(self, image, target_size):
        """等比例缩放图像（长轴匹配目标尺寸）"""
        width, height = image.size
        long_side = max(width, height)
        
        if long_side <= target_size:
            return image
        
        scale = target_size / long_side
        new_size = (int(width * scale), int(height * scale))
        return image.resize(new_size, Image.LANCZOS)
    
    def process_image(self, file_path):
        """处理单个图像：缩放+通道映射"""
        try:
            with Image.open(file_path) as img:
                # 转换为RGBA并确保有alpha通道
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 缩放图像
                img = self.resize_image(img, self.target_size.get())
                
                # 分离通道
                r, g, b, a = img.split()
                channels = {'R': r, 'G': g, 'B': b, 'A': a}
                
                # 应用通道映射
                new_channels = []
                for c in ['R', 'G', 'B', 'A']:
                    channel_source = self.channel_map[c].get()
                    channel_img = channels[channel_source]
                    # 应用反转
                    if self.invert_options[c].get():
                        channel_img = ImageOps.invert(channel_img)
                    new_channels.append(channel_img)

                new_img = Image.merge('RGBA', new_channels)
                new_img_noalpha = Image.merge('RGB', new_channels[:3]) 
                
                # 确定输出路径和格式
                file_dir, file_name = os.path.split(file_path)
                name, ext = os.path.splitext(file_name)
                
                if self.overwrite_source.get():
                    # 覆盖源文件，使用源文件格式
                    output_format = ext[1:].upper()  # 去掉点并转为大写
                    if output_format == 'JPG':
                        output_format = 'JPEG'
                    new_path = file_path
                else:
                    # 不覆盖源文件，使用选择的格式
                    output_format = self.output_format.get()
                    new_path = os.path.join(file_dir, f"{name}.{output_format.lower()}")
                
                # 保存结果
                if output_format == 'JPEG':
                    new_img_noalpha.save(new_path, format=output_format, quality=95)
                else:
                    new_img.save(new_path, format=output_format)
                
                return new_path, None
        except Exception as e:
            return None, str(e)
    
    def process_images(self):
        if not self.files_to_process:
            tk.messagebox.showwarning("无文件", "请先添加要处理的图像文件")
            return
        
        # 创建进度窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("处理中...")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # 进度标签
        progress_label = ttk.Label(progress_window, text="处理进度:")
        progress_label.pack(pady=10)
        
        # 进度条
        progress = ttk.Progressbar(
            progress_window, 
            orient='horizontal',
            length=300, 
            mode='determinate'
        )
        progress.pack(pady=10)
        
        # 状态标签
        status_label = ttk.Label(progress_window, text="准备开始处理")
        status_label.pack(pady=10)
        
        # 结果列表
        result_frame = ttk.Frame(progress_window)
        result_frame.pack(fill='both', expand=True, padx=20)
        result_listbox = tk.Listbox(result_frame, height=5)
        result_listbox.pack(fill='both', expand=True, pady=5)
        
        progress_window.update()
        
        # 处理图像
        total = len(self.files_to_process)
        success_count = 0
        
        for i, file_path in enumerate(self.files_to_process):
            # 更新进度
            progress_value = int((i + 1) / total * 100)
            progress['value'] = progress_value
            status_label.config(text=f"处理: {os.path.basename(file_path)} ({progress_value}%)")
            progress_window.update()
            
            # 处理图像
            result_path, error = self.process_image(file_path)
            
            if result_path:
                result_listbox.insert(tk.END, f"成功: {os.path.basename(result_path)}")
                success_count += 1
            else:
                result_listbox.insert(tk.END, f"失败: {os.path.basename(file_path)} ({error})")
            
            # 滚动到最新结果
            result_listbox.yview_moveto(1)
            progress_window.update()
        
        # 完成处理
        status_label.config(text=f"处理完成: {success_count}/{total} 成功")
        ttk.Button(
            progress_window, 
            text="关闭", 
            command=progress_window.destroy
        ).pack(pady=10)
        
        # 完成后清空文件列表
        self.files_to_process = []
        self.update_file_listbox()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()