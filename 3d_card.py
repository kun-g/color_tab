from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
import csv
import os

# 参数设置
LABEL_SIZE = 30 * mm  # 增大标签尺寸
MARGIN = 1 * mm
GAP = 0.5 * mm
CORNER_RADIUS = 2 * mm
BORDER_WIDTH = 0.5 * mm
FONT_SIZE = 16  # 点数
FIRST_LINE_FONT_SIZE = 16
FIRST_LINE_SPACING = 0.5 * mm # 首行行间距
LINE_SPACING = 0.2 * mm
PADDING_LEFT = 0.9 * mm
PADDING_TOP = 1.0 * mm

def find_system_font():
    potential_fonts = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    
    for font_path in potential_fonts:
        if os.path.exists(font_path):
            return font_path
    
    raise FileNotFoundError("No suitable system font found")

def get_max_font_size(c, text, max_width, max_height, font_name, start_size):
    font_size = start_size
    n_lines = len(text.split('\n'))
    longest_line = max(text.split('\n'), key=len)
    while font_size > 1:
        c.setFont(font_name, font_size)
        text_width = c.stringWidth(longest_line, font_name, font_size)
        text_height = (n_lines * font_size) + (n_lines - 1) * LINE_SPACING
        if text_width <= max_width and text_height <= max_height:
            return font_size
        font_size -= 0.5
    return 1

def create_label(c, x, y, label_data):
    # 拼接厂商和材料
    first_line = f"{label_data[0]}/{label_data[1]}"
    
    # 绘制圆角矩形
    c.roundRect(x, y, LABEL_SIZE, LABEL_SIZE, CORNER_RADIUS)
    
    # 计算最大可用字体大小
    max_width = LABEL_SIZE - 2 * PADDING_LEFT
    max_height = LABEL_SIZE - 2 * PADDING_TOP

    font_size = FIRST_LINE_FONT_SIZE
    # 绘制文字
    c.setFont('CustomFont', FIRST_LINE_FONT_SIZE)
    
    # 绘制第一行（居中）
    first_line_width = c.stringWidth(first_line, 'CustomFont', font_size)
    text_x = x + (LABEL_SIZE - first_line_width) / 2
    text_y = y + LABEL_SIZE - PADDING_TOP - font_size
    c.drawString(text_x, text_y, first_line)

    # 画一条横线
    c.setLineWidth(BORDER_WIDTH)
    c.line(x + PADDING_LEFT, text_y - FIRST_LINE_SPACING*2, x + LABEL_SIZE - PADDING_LEFT, text_y - FIRST_LINE_SPACING*2)

    all_text = '\n'.join(label_data[2:])
    font_size = get_max_font_size(c, all_text, max_width, max_height, 'CustomFont', FONT_SIZE)

    n_lines = len(label_data[2:])
    text_y -= (LABEL_SIZE-FIRST_LINE_FONT_SIZE-PADDING_TOP - FIRST_LINE_SPACING*5 - font_size*n_lines)/2

    # 绘制剩余行
    text_x = x + PADDING_LEFT
    text_y -= (font_size + LINE_SPACING)
    for line in label_data[2:]:
        c.drawString(text_x, text_y, line)
        text_y -= (font_size + LINE_SPACING)

def create_label_sheet(labels, output_file):
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    # 注册字体
    font_path = find_system_font()
    pdfmetrics.registerFont(TTFont('CustomFont', font_path))
    
    cols = int((width - 2*MARGIN) // (LABEL_SIZE + GAP))
    rows = int((height - 2*MARGIN) // (LABEL_SIZE + GAP))

    for i, label_data in enumerate(labels):
        row = i // cols
        col = i % cols
        
        x = MARGIN + col * (LABEL_SIZE + GAP)
        y = height - MARGIN - (row + 1) * (LABEL_SIZE + GAP)

        create_label(c, x, y, label_data)

    c.save()

def read_labels_from_csv(filename):
    labels = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过标题行
        for row in reader:
            labels.append(row)
    return labels

if __name__ == "__main__":
    labels = read_labels_from_csv('labels.csv')
    create_label_sheet(labels, 'output.pdf')
