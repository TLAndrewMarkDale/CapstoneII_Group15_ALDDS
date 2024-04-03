from fpdf import FPDF
from datetime import datetime
import cv2
import os
from fpdf.enums import XPos, YPos
from ultralytics import YOLO
model_loc = "best.pt" 
model = YOLO(model_loc) # Loading best model
names = model.names
def create_report(images):
    pdf = FPDF()
    d = datetime.now()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    page_width = pdf.epw
    pdf.set_font("Helvetica", "B", size=24)
    pdf.image("drone_images/aldds_png.png", x=pdf.w/4, y=pdf.w/4, w=pdf.w/2, h=pdf.w/2)
    pdf.cell(200, 10, txt="ALDDS Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.cell(200, 10, text=f"Time created: {d.year}/{d.month}/{d.day} {d.hour}:{d.minute}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    image_count = 1
    for image in images:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", size=16)
        pdf.cell(200, 10, text=f"Image {image_count}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        img = cv2.cvtColor(image[0], cv2.COLOR_RGB2BGR)
        detections = model(img)[0] # what is detected in the frame
        detections_above_conf = 0
        for detect in detections.boxes.data.tolist():
            confidence = detect[4] 
            # If the confidence of the model is below 50%, skip it
            if float(confidence) < .5: 
                continue
            detections_above_conf += 1
            xmin, ymin, xmax, ymax = int(detect[0]), int(detect[1]), int(detect[2]), int(detect[3])
            # Creating a bounding box
            bounding_box = cv2.rectangle(img, 
                                         (xmin, ymin), 
                                         (xmax, ymax), 
                                         (0, 0, 255), 
                                         2) 

            # This code simply adds text to the box.
            cv2.putText(bounding_box, 
                        names[detect[5]], 
                        (xmin, ymin-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.6, 
                        (36,255,12), 
                        2)
        height, width, _ = img.shape
        cv2.imwrite(f"drone_images/temp{image_count}.png", img)
        ratio = height/width
        pdf.image(f"drone_images/temp{image_count}.png", x=(page_width - pdf.w * .75) - 10, y=50, w=pdf.w * .75, h=round(pdf.w*.75*ratio))
        pdf.set_font("Helvetica", size=12)
        pdf.cell(200, 10, text=f"Image taken {image[1]} seconds into flight", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.cell(200, 10, text=f"Time taken: {image[2].year}/{image[2].month}/{image[2].day} {image[2].hour}:{image[2].minute}:{image[2].second}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.cell(200, 10, text=f"Number of detections: {detections_above_conf}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        pdf.ln(100)
        image_count += 1
    pdf.output(f"ALDDS_report_{d.year}-{d.month}-{d.day}_{d.hour}{d.minute}.pdf")


