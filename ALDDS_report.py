from fpdf import FPDF
from datetime import datetime
import cv2
import os

def create_report(images):
    pdf = FPDF()
    d = datetime.now()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", size=24)
    pdf.image("drone_images/aldds_icon.png", x=10, y=8, w=400, h=400)
    pdf.cell(200, 10, txt="ALDDS Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Time created: {d.year}/{d.month}/{d.day} {d.hour}:{d.minute}", ln=True, align='C')
    pdf.ln(10)
    image_count = 1
    for image in images:
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt=f"Image {image_count}", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Image taken {image[1]} seconds into flight", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Time taken: {image[2].year}/{image[2].month}/{image[2].day} {image[2].hour}:{image[2].minute}:{image[2].second}", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        img = cv2.cvtColor(image[0], cv2.COLOR_RGB2BGR)
        height, width, _ = img.shape
        cv2.imwrite(f"drone_images/temp{image_count}.png", img)
        pdf.image(f"drone_images/temp{image_count}.png", x=10, y=10, w=pdf.w/2, h=pdf.h/4)
        pdf.ln(100)
        image_count += 1
    pdf.output(f"ALDDS_report_{d.year}-{d.month}-{d.day}_{d.hour}{d.minute}.pdf")