import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import os
from PIL import Image

selected_image = ""
entry_name = None
entry_scale = None
global image

def select_image(entry):
    global selected_image
    file_path = filedialog.askopenfilename(
        title="选择图像文件",
        filetypes=[("TIF files", "*.tif *.tiff")]
    )
    if file_path:
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if image is not None:
            selected_image = file_path
            entry.delete(0, tk.END)
            entry.insert(0, selected_image)
        else:
            messagebox.showerror("错误", "所选文件无法读取，请选择一个有效的图像文件。")

def process_image(show_message=True):
    global image, image_name, scale, directory, white_bar_height
    image_name = entry_name.get()
    scale = entry_scale.get()
    if not selected_image:
        if show_message:
            messagebox.showerror("错误", "请先选择一个图像文件。")
        return
    directory = os.path.dirname(selected_image)
    if not os.path.exists(directory):
        if show_message:
            messagebox.showerror("错误", "所选文件的目录不存在。")
        return
    image = cv2.imread(selected_image, cv2.IMREAD_UNCHANGED)
    if image is None:
        if show_message:
            messagebox.showerror("错误", "无法读取所选图像文件，请检查文件路径或文件完整性。")
        return
    lower_green = np.array([50, 50, 50])
    upper_green = np.array([100, 255, 255])
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        length = w
        height, width, _ = image.shape
        white_bar_height = int(height * 0.02)
        white_bar = np.ones((white_bar_height, length), dtype=np.uint8) * 255
        white_bar_half_width = length // 2
        white_bar_position = (100 - white_bar_half_width, height - white_bar_height - 90)
        image = cv2.rectangle(image, white_bar_position, (white_bar_position[0] + length, white_bar_position[1] + white_bar_height), (255, 255, 255), -1)
        font = cv2.FONT_HERSHEY_TRIPLEX
        text = scale
        text_position = (white_bar_position[0], white_bar_position[1] - int(white_bar_height * 1.2))
        font_scale = 0.7
        text_color = (255, 255, 255)
        line_type = 2
        cv2.putText(image, text, text_position, font, font_scale, text_color, line_type)
        cv2.imwrite(os.path.join(directory, f'{image_name}.tif'), image)
        processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(processed_image)
        width, height = image.size
        new_height = 690
        crop_box = (0, 0, width, new_height)
        cropped_image = image.crop(crop_box)
        resized_image = cropped_image.resize((1024, new_height), Image.Resampling.LANCZOS)
        resized_image.save(os.path.join(directory, f'{image_name}.png'), 'PNG')
        if show_message:
            messagebox.showinfo("完成", f"图片已处理并保存为：\n{os.path.join(directory, f'{image_name}.tif')} 和 {os.path.join(directory, f'{image_name}.png')}")
    else:
        if show_message:
            messagebox.showerror("错误", "在图像中未找到轮廓。")

def process_image_black(show_message=True):
    global image, image_name, scale, directory, white_bar_height
    process_image(show_message=False)
    if not isinstance(image, Image.Image):
        if show_message:
            messagebox.showerror("错误", "image 变量不是 PIL Image 对象。")
        return
    np_image = np.array(image.convert('RGB'))
    height, width = np_image.shape[0:2]
    black_bar_height = white_bar_height * 5
    black_bar_length = int(width * 0.2)
    black_bar = np.zeros((black_bar_height, black_bar_length, 3), dtype=np.uint8)
    black_bar_position = (0, height - black_bar_height - (height // 10))
    np_image[black_bar_position[1]: black_bar_position[1] + black_bar_height,
    max(0, black_bar_position[0]):min(width, black_bar_position[0] + black_bar_length)] = black_bar
    image = Image.fromarray(np_image)
    black_bg_image_path = os.path.join(directory, f'{image_name}_black_bg.tif')
    cv2.imwrite(black_bg_image_path, cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR))
    global selected_image
    selected_image = black_bg_image_path
    entry_image.delete(0, tk.END)
    entry_image.insert(0, selected_image)
    process_image(show_message=False)
    if show_message:
        messagebox.showinfo("完成", f"图片已处理并保存为：\n{black_bg_image_path}")

def batch_process():
    directory = filedialog.askdirectory(title="选择要处理的目录")
    if not directory:
        return
    for filename in os.listdir(directory):
        if filename.endswith(('.tif', '.tiff')):
            image_path = os.path.join(directory, filename)
            image_name = os.path.splitext(filename)[0]
            folder_path = os.path.join(directory, image_name)
            os.makedirs(folder_path, exist_ok=True)
            new_image_path = os.path.join(folder_path, filename)
            os.rename(image_path, new_image_path)
            global selected_image
            selected_image = new_image_path
            process_image_black(show_message=False)

# 创建主窗口
root = tk.Tk()
root.title("图像处理工具")

# 创建一个按钮用于批量处理图片
button_batch_process = tk.Button(root, text="批量处理", command=batch_process)
button_batch_process.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

# 创建一个标签和输入框用于选择图像文件
label_image = tk.Label(root, text="选择电镜图像.tif文件（文件路径不能包含中文）：")
entry_image = tk.Entry(root, width=50)
button_select = tk.Button(root, text="浏览", command=lambda: select_image(entry_image))

# 创建一个标签和输入框用于输入图片名称
label_name = tk.Label(root, text="输入图片处理后新文件的文件名（最好没中文）：")
entry_name = tk.Entry(root, width=50)

# 创建一个标签和输入框用于输入标尺
label_scale = tk.Label(root, text="输入标尺 （如：300 nm，涉及\u03BCm请手动绘图）：")
entry_scale = tk.Entry(root, width=50)

# 创建一个按钮用于处理图片
button_process = tk.Button(root, text="处理图片", command=lambda: process_image(show_message=True))

# 创建一个按钮用于处理图片并添加黑色背景
button_process_black = tk.Button(root, text="处理图片+黑色背景", command=lambda: process_image_black(show_message=True))
button_process_black.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

# 布局
label_image.grid(row=0, column=0, padx=10, pady=5, sticky='e')
entry_image.grid(row=0, column=1, padx=10, pady=5)
button_select.grid(row=0, column=2, padx=10, pady=5)

label_name.grid(row=1, column=0, padx=10, pady=5, sticky='e')
entry_name.grid(row=1, column=1, padx=10, pady=5)

label_scale.grid(row=2, column=0, padx=10, pady=5, sticky='e')
entry_scale.grid(row=2, column=1, padx=10, pady=5)

button_process.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

# 运行主循环
root.mainloop()
