import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.patches import Rectangle
import os

def normalize_data(intensities):
    max_intensity = max(intensities)
    return [intensity / max_intensity for intensity in intensities]

def plot_xrd_data(file_info_list, xytext_x, xytext_y):
    # 创建一个图形窗口
    fig, ax = plt.subplots()

    # 初始化最大字号大小和最小角度值
    max_font_size = 0
    min_angle = float('inf')  # 初始化为无穷大，以便能被实际数据替换

    # 遍历文件信息列表并为每个文件绘制数据
    for file_info in file_info_list:
        filename = file_info['file_path']
        label_name = file_info['label_name']
        line_color = file_info['line_color']
        line_width = file_info['line_width']
        offset = float(file_info['offset'])
        label_font_size_str = file_info['label_font_size']  # 假设字号存储为字符串
        label_font_size = int(label_font_size_str)  # 转换为整数

        # 更新最大字号大小
        max_font_size = max(label_font_size,max_font_size)

        # 初始化一个空列表来保存数据
        xrd_data = []
        max_angle = 0  # 用于记录最大角度值

        # 打开文件进行读取
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('*'):
                    parts = line.split()
                    if len(parts) == 2:
                        angle = float(parts[0])
                        intensity = float(parts[1])
                        xrd_data.append((angle, intensity))
                        max_angle = max(max_angle, angle)

        # 提取角度和强度
        angles, intensities = zip(*xrd_data)

        # 对强度数据进行归一化处理
        intensities_normalized = normalize_data(intensities)

        # 对强度数据进行高斯平滑处理
        intensities_smooth = gaussian_filter(intensities_normalized, sigma=1)

        if len(file_info_list)>2:
            # 根据偏移量调整纵坐标范围并绘制数据图
            line, = ax.plot(angles, intensities_smooth + offset, color=line_color,
                            linewidth=line_width, alpha=1)

            # 使用调整后的xytext值
            ax.annotate(label_name, xy=(angles[-1], intensities_smooth[-1] + offset),
                        xytext=(xytext_x, xytext_y), textcoords='offset points',
                        fontsize=max_font_size)
        else:
            # 根据偏移量调整纵坐标范围并绘制数据图
            ax.plot(angles, intensities_smooth + offset, color=line_color,
                    label=label_name, linewidth=line_width, alpha=1)

            legend = ax.legend(fontsize=max_font_size, reverse=True, loc='upper right', bbox_to_anchor=(1, 1),
                               frameon=False)

        # 更新最小角度值
        min_angle = min(min_angle, min(angles) if angles else 0)

    # 设置边框加粗
    plt.setp(ax.spines.values(), linewidth=3)
    # 设置全局字体加粗
    plt.rcParams['font.weight'] = 'semibold'
    # 设置全局的坐标轴标签字号
    ax.tick_params(axis='both', labelsize=max_font_size)
    plt.rcParams['font.sans-serif'] = ['Arial']

    # 设置全局的坐标轴标签字号和刻度的粗细
    ax.tick_params(axis='both', labelsize=max_font_size, length=12, width=4)

    # 添加图表标题和坐标轴标签，并设置字号
    ax.set_xlabel('2 Theta (Deg.)', fontsize=max_font_size, fontweight='semibold')
    ax.set_ylabel('Intensity (a.u.)', fontsize=max_font_size, fontweight='semibold')

    # 取消纵坐标刻度
    ax.set_yticks([])
    # 纵坐标标签左移
    ax.yaxis.set_label_coords(-0.02, 0.5)  # 向左移动标签
    # 设置横坐标的起点和终点
    ax.set_xlim([0 if min_angle == float('inf') else min_angle, max_angle])

    # 反转图例项的顺序，并添加图例
    #ax.legend(fontsize=max_font_size, reverse=True)

    # 显示图表
    plt.show()


class XRDPlotApplication:

    def __init__(self, root):
        self.root = root
        self.root.title("XRD Plot Xu")
        self.files_info = {}
        self.entry_widgets = {}
        self.create_gui_components()
        self.xytext_x = -125
        self.xytext_y = 15

    def create_gui_components(self):
        self.column_headers = ("序号", "文件路径", "图例名", "字号", "线条颜色", "线条粗细", "偏移", "操作1","操作2")
        for current_column, header in enumerate(self.column_headers):
            tk.Label(self.root, text=header, anchor='center').grid(row=0, column=current_column, padx=10, pady=5, sticky="ew")

        for i in range(1, 11):
            self.create_file_row(i)

        self.batch_select_files_button = tk.Button(self.root, text="批量选择文件", command=self.on_batch_select_files)
        self.batch_select_files_button.grid(row=11, columnspan=len(self.column_headers), padx=10, pady=5, sticky="ew")

        self.plot_image_button = tk.Button(self.root, text="绘制图像", command=self.on_plot_image)
        self.plot_image_button.grid(row=12, columnspan=len(self.column_headers), padx=10, pady=5, sticky="ew")

        self.info_frame = tk.Frame(self.root)
        self.info_frame.grid(row=0, column=len(self.column_headers), rowspan=12, padx=10, pady=5, sticky="ns")

        self.info_text = tk.Text(self.info_frame, wrap=tk.WORD, width=55, height=40)
        self.info_text.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.info_text.insert(tk.END, """默认字体：Arial。默认字号为30。
                \n默认线条粗细为3。默认偏移量为0。
                \n调节字号仅支持共同调节（只能向上条调节,>30）,程序会选择最大值。
                \n线条粗细支持分别调节。
                \n当文件数大于3时，图例格式变为跟随线条格式
                \n图例偏移量的坐标原点是线条的尾端，修改后点击按钮——“调整图像偏移量”，目前仅支持同步调节。
                \n颜色：可以使用颜色名来指定线条颜色,也可以使用HTML颜色代码，如 #FF0000（红色）。
                \n下角标命名规则：$_X$
                \n\ntip1：可以通过最大化窗口后保存图片，来固定图片的尺寸。
                \n\ntip2：可通过放大框选，将图片调整到想展示的细节。
                \n\nbug：打开程序第一次绘制时标签会显示为加粗的效果，关掉图片再次绘制即可""")

        self.info_text.config(state=tk.DISABLED)
        # 添加新的xytext调节按钮和输入框
        self.xytext_label = tk.Label(self.root, text="图例偏移量 (xytext):", anchor='center')
        self.xytext_label.grid(row=13, column=0, padx=10, pady=5, sticky="ew")

        self.xytext_x_entry = tk.Entry(self.root, width=5)
        self.xytext_x_entry.grid(row=13, column=1, padx=10, pady=5, sticky="ew")
        self.xytext_x_entry.insert(0, "-125")  # 默认x偏移量

        self.xytext_y_entry = tk.Entry(self.root, width=5)
        self.xytext_y_entry.grid(row=13, column=2, padx=10, pady=5, sticky="ew")
        self.xytext_y_entry.insert(0, "15")  # 默认y偏移量

        self.adjust_xytext_button = tk.Button(self.root, text="调整图例偏移量", command=self.on_adjust_xytext)
        self.adjust_xytext_button.grid(row=13, column=3, padx=10, pady=5, sticky="ew")

    def on_adjust_xytext(self):
        # 读取xytext的x和y偏移量
        xytext_x = self.xytext_x_entry.get()
        xytext_y = self.xytext_y_entry.get()

        # 检查输入是否为数字
        try:
            xytext_x = int(xytext_x)
            xytext_y = int(xytext_y)
        except ValueError:
            messagebox.showerror("错误", "偏移量输入无效，请输入数字。")
            return

        # 更新xytext值
        self.xytext_x = xytext_x
        self.xytext_y = xytext_y

    def create_file_row(self, row, file_path=None):
        tk.Label(self.root, text=f"{row}", width=1, anchor='center').grid(row=row, column=0, padx=10, pady=5, sticky="ew")

        file_path_entry = tk.Entry(self.root)
        file_path_entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        self.entry_widgets[(row, 1)] = file_path_entry

        for col in range(2, len(self.column_headers) - 2):
            entry = tk.Entry(self.root)
            entry.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            self.entry_widgets[(row, col)] = entry

        color_options = ["Pink","Red", "Blue", "Purple","Orange", "Lime"]
        default_color_index = row % len(color_options)  # 为每行选择一个默认颜色
        color_entry = tk.Entry(self.root)
        color_entry.grid(row=row, column=4, padx=10, pady=5, sticky="ew")  # 假设颜色栏在第四列
        color_entry.insert(0, color_options[default_color_index])  # 设置默认颜色
        self.entry_widgets[(row, 4)] = color_entry

        # 创建偏移量选择的文本框，并为其设置默认偏移量
        offset_options = ["9","0", "1", "2", "3", "4", "5", "6", "7", "8"]
        default_offset_index = row % len(offset_options)  # 为每行选择一个默认偏移量
        offset_entry = tk.Entry(self.root)
        offset_entry.grid(row=row, column=6, padx=10, pady=5, sticky="ew")  # 假设偏移量栏在第六列
        offset_entry.insert(0, offset_options[default_offset_index])  # 设置默认偏移量
        self.entry_widgets[(row, 6)] = offset_entry

        add_file_button = tk.Button(self.root, text="选择文件", command=lambda r=row: self.add_file(r))
        add_file_button.grid(row=row, column=len(self.column_headers) -2, padx=10, pady=5, sticky="ew")

        # 新增的移除文件按钮
        remove_file_button = tk.Button(self.root, text="移除文件", command=lambda r=row: self.remove_file(r))
        remove_file_button.grid(row=row, column=len(self.column_headers)-1, padx=10, pady=5, sticky="ew")
        if file_path:
            file_path_entry.delete(0, tk.END)
            file_path_entry.insert(0, file_path)
            file_name = os.path.basename(file_path)
            self.entry_widgets[(row, 2)].delete(0, tk.END)
            self.entry_widgets[(row, 2)].insert(0, os.path.splitext(file_name)[0])

    def add_file(self, row):
        file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("Text files", "*.txt"), ("Integer files", "*.int")])
        if file_path:
            file_name = os.path.basename(file_path)
            file_path_entry = self.entry_widgets.get((row, 1))
            file_path_entry.delete(0, tk.END)
            file_path_entry.insert(0, file_path)
            self.entry_widgets[(row, 2)].delete(0, tk.END)
            self.entry_widgets[(row, 2)].insert(0, os.path.splitext(file_name)[0])

    def remove_file(self, row):
        # 移除文件信息
        file_path_entry = self.entry_widgets.get((row, 1), None)
        if file_path_entry:
            file_path_entry.delete(0, tk.END)  # 清空文件路径输入框

        # 更新其他相关输入框
        for col in range(2, len(self.column_headers)):
            entry = self.entry_widgets.get((row, col), None)
            if entry:
                entry.delete(0, tk.END)  # 清空该行的其他输入框

    def on_plot_image(self):
        file_info_list = []
        for row in range(1, 11):
            file_path_entry = self.entry_widgets.get((row, 1), None)
            if file_path_entry and file_path_entry.get().strip():
                file_info = {
                    'file_path': file_path_entry.get(),
                    'label_name': self.entry_widgets.get((row, 2), '').get().strip() or os.path.splitext(os.path.basename(file_path_entry.get()))[0],
                    'label_font_size': self.entry_widgets.get((row, 3), '').get().strip() or '30',
                    'line_color': self.entry_widgets.get((row, 4), '').get().strip() or 'blue',
                    'line_width': self.entry_widgets.get((row, 5), '').get().strip() or '3',
                    'offset': self.entry_widgets.get((row, 6), '').get().strip() or '0',
                }
                file_info_list.append(file_info)

        if file_info_list:
            plot_xrd_data(file_info_list, self.xytext_x, self.xytext_y)
        else:
            messagebox.showerror("错误", "请选择至少一个文件进行绘图")

    def on_batch_select_files(self):
        # 弹出文件选择对话框，允许多选
        file_paths = filedialog.askopenfilenames(title="批量选择文件",
                                                 filetypes=[("Text files", "*.txt"), ("Integer files", "*.int")])
        if file_paths:
            for file_path in file_paths:
                # 为每个选择的文件找到一个空行
                empty_row = self.find_empty_row()
                if empty_row is not None:
                    # 由于是批量选择，不需要再次显示选择文件对话框，所以不传递 file_path 给 create_file_row
                    self.create_file_row(empty_row)
                    # 手动填充文件路径和图例名
                    file_path_entry = self.entry_widgets.get((empty_row, 1))
                    file_path_entry.delete(0, tk.END)
                    file_path_entry.insert(0, file_path)

                    # 设置图例名为文件名（不含扩展名）
                    file_name = os.path.basename(file_path)
                    label_name_entry = self.entry_widgets.get((empty_row, 2))
                    label_name_entry.delete(0, tk.END)
                    label_name_entry.insert(0, os.path.splitext(file_name)[0])

    def find_empty_row(self):
        for row in range(1, 11):
            file_path_entry = self.entry_widgets.get((row, 1), None)
            if not file_path_entry or file_path_entry.get().strip() == '':
                return row
        messagebox.showerror("错误", "已达到最大文件数量限制。")
        return None

    # 主程序
def main():
    root = tk.Tk()
    app = XRDPlotApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()