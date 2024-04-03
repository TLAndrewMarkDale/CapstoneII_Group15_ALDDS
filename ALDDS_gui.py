# import Tkinter to create our GUI.
from tkinter import Tk, Label, Button, Frame, Canvas, PhotoImage
# import openCV for receiving the video frames
import cv2
# make imports from the Pillow library for displaying the video stream with Tkinter.
from PIL import Image, ImageTk
# Import the tello module
from djitellopy import tello
# Import threading for our keyboard controller
import threading
from pathlib import Path

from datetime import datetime
# Importing our keyboard controller
from ALDDS_controller import KeyboardController

# Importing the queue module for our keyboard controller, to communicate between threads
import queue

from ALDDS_report import create_report


# Importing ctypes to set the DPI awareness, otherwise the GUI will be blurry
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"final_gui\build\assets\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Model imports. Importing the YOLO model from ultralytics
# Importing torch to check if we have a GPU available

from ultralytics import YOLO
import torch
device = "0" if torch.cuda.is_available() else "cpu"
if device == "0":
    torch.cuda.set_device(0)
print(device)
model_loc = "models/yolov8s_200epochs/weights/best.pt"
model = YOLO(model_loc)
names = model.names


class DroneGUI:
    def __init__(self):
        self.window = Tk()

        # Creating the queues for the keyboard controller
        self.enable_cv_queue = queue.Queue()
        self.image_queue = queue.Queue()
        self.detect = False

        # Connecting to the drone, setting the speed and starting the video stream
        self.drone = tello.Tello()
        self.drone.connect()
        self.drone.streamon()
        self.frame = self.drone.get_frame_read()
        self.drone.speed = 50

        # Setting up the GUI window
        # After Tello to ensure that it is connected
        self.window.title("ALDDS")
        self.window.geometry("1440x899")
        self.window.configure(bg = "#FFFFFF")
        self.window.iconphoto(False, PhotoImage(file="drone_images/aldds_icon.png"))
        self.window.resizable(False, False)
        self.canvas = Canvas(
            self.window,
            bg = "#FFFFFF",
            height = 899,
            width = 1440,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        # Placing the canvas
        self.canvas.place(x = 0, y = 0)

        # Create the input frame, which will be used to capture key presses
        # These captures allow us to show the user what keys are being pressed
        self.input_frame = Frame(self.window)

        self.keyboard_thread = KeyboardController(flip_cv=self.enable_cv_queue, drone=self.drone)

    def run_app(self):
        try:
            self.canvas.create_rectangle(
            0.0,
            0.0,
            1440.0,
            899.9999389648438,
            fill="#303133",
            outline="")

            image_image_1 = PhotoImage(
                file=relative_to_assets("image_1.png"))
            self.video_image = self.canvas.create_image(
                448.875,
                307.25006103515625,
                image=image_image_1
            )

            image_image_2 = PhotoImage(
                file=relative_to_assets("image_2.png"))
            image_2 = self.canvas.create_image(
                448.875,
                756.375,
                image=image_image_2
            )

            self.canvas.create_text(
                145.12490844726562,
                723.375,
                anchor="nw",
                text="ALDDS",
                fill="#FFFFFF",
                font=("Inter Bold", 35 * -1)
            )

            self.canvas.create_text(
                59.62493896484375,
                788.6249389648438,
                anchor="nw",
                text="Autonomous Litter Detection and Delivery System. ",
                fill="#FFFFFF",
                font=("Inter", 13 * -1)
            )

            image_image_3 = PhotoImage(
                file=relative_to_assets("image_3.png"))
            image_3 = self.canvas.create_image(
                92.875,
                728.6249389648438,
                image=image_image_3
            )

            image_image_4 = PhotoImage(
                file=relative_to_assets("image_4.png"))
            image_4 = self.canvas.create_image(
                1179.6250610351562,
                270.25006103515625,
                image=image_image_4
            )

            self.canvas.create_text(
                1132.8748779296875,
                295.8749694824219,
                anchor="nw",
                text="Roll (Degrees)",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
            )

            self.rolltext = self.canvas.create_text(
                1132.8748779296875,
                313.8749694824219,
                anchor="nw",
                text="N/A °",
                fill="#FE8944",
                font=("Inter Bold", 12 * -1)
            )

            self.flight_time = self.canvas.create_text(
                1274.6251220703125,
                313.8749694824219,
                anchor="nw",
                text="N/A s",
                fill="#FE8944",
                font=("Inter Bold", 12 * -1)
            )

            self.canvas.create_text(
                1132.8748779296875,
                349.875,
                anchor="nw",
                text="Pitch (Degrees)",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
            )

            self.pitch_text = self.canvas.create_text(
                1132.8748779296875,
                367.8749694824219,
                anchor="nw",
                text="N/A °",
                fill="#FE8944",
                font=("Inter Bold", 12 * -1)
            )

            self.canvas.create_text(
                1274.6251220703125,
                349.875,
                anchor="nw",
                text="Barometer",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
            )

            self.barometer = self.canvas.create_text(
                1274.6251220703125,
                367.8749694824219,
                anchor="nw",
                text="N/A cm",
                fill="#FE8944",
                font=("Inter Bold", 12 * -1)
            )

            self.canvas.create_text(
                1274.6251220703125,
                400.5,
                anchor="nw",
                text="Height",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
            )

            self.height = self.canvas.create_text(
                1274.6251220703125,
                418.49993896484375,
                anchor="nw",
                text="N/A cm",
                fill="#FE8944",
                font=("Inter Bold", 12 * -1)
            )

            self.canvas.create_text(
                1132.8748779296875,
                400.5,
                anchor="nw",
                text="Yaw (Degrees)",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
            )

            self.yaw_text = self.canvas.create_text(
                1132.8748779296875,
                418.49993896484375,
                anchor="nw",
                text="N/A °",
                fill="#FE8944",
                font=("Inter Bold", 12 * -1)
            )

            image_image_5 = PhotoImage(
                file=relative_to_assets("image_5.png"))
            image_5 = self.canvas.create_image(
                1179.4999389648438,
                120.49996948242188,
                image=image_image_5
            )

            self.battery_text = self.canvas.create_text(
                1031.6248779296875,
                113.62496948242188,
                anchor="nw",
                text="N/A%",
                fill="#FFFFFF",
                font=("Inter", 12 * -1)
            )

            image_image_6 = PhotoImage(
                file=relative_to_assets("image_6.png"))
            image_6 = self.canvas.create_image(
                1011.1248168945312,
                119.99996948242188,
                image=image_image_6
            )

            self.canvas.create_text(
                985.4999389648438,
                75.37496948242188,
                anchor="nw",
                text="Battery",
                fill="#FFFFFF",
                font=("Inter Bold", 15 * -1)
            )

            self.temperature = self.canvas.create_text(
                1312.8748779296875,
                112.49996948242188,
                anchor="nw",
                text="N/A ° C",
                fill="#FFFFFF",
                font=("Inter", 12 * -1)
            )

            self.canvas.create_rectangle(
                1296.0000001192093,
                109.12503063678741,
                1297.125,
                131.6250286102295,
                fill="#FFFFFF",
                outline="")

            self.battery_mah = self.canvas.create_text(
                1179.0,
                112.49996948242188,
                anchor="nw",
                text="N/A / 1100 mAh",
                fill="#FFFFFF",
                font=("Inter", 12 * -1)
            )

            image_image_7 = PhotoImage(
                file=relative_to_assets("image_7.png"))
            image_7 = self.canvas.create_image(
                1179.6250610351562,
                703.5,
                image=image_image_7
            )

            image_image_8 = PhotoImage(
                file=relative_to_assets("image_8.png"))
            image_8 = self.canvas.create_image(
                999.8749389648438,
                576.8749389648438,
                image=image_image_8
            )

            image_image_9 = PhotoImage(
                file=relative_to_assets("image_9.png"))
            image_9 = self.canvas.create_image(
                999.8749389648438,
                832.2499389648438,
                image=image_image_9
            )

            self.canvas.create_text(
                995.6249389648438,
                823.4999389648438,
                anchor="nw",
                text="+",
                fill="#000000",
                font=("Inter", 13 * -1)
            )

            image_image_10 = PhotoImage(
                file=relative_to_assets("image_10.png"))
            image_10 = self.canvas.create_image(
                1363.249755859375,
                832.2499389648438,
                image=image_image_10
            )

            image_image_11 = PhotoImage(
                file=relative_to_assets("image_11.png"))
            image_11 = self.canvas.create_image(
                1363.249755859375,
                576.8749389648438,
                image=image_image_11
            )

            self.canvas.create_text(
                1358.9998779296875,
                568.1249389648438,
                anchor="nw",
                text="+",
                fill="#000000",
                font=("Inter", 13 * -1)
            )

            self.canvas.create_text(
                1358.9998779296875,
                823.4999389648438,
                anchor="nw",
                text="+",
                fill="#000000",
                font=("Inter", 13 * -1)
            )

            self.canvas.create_text(
                995.6249389648438,
                568.1249389648438,
                anchor="nw",
                text="+",
                fill="#000000",
                font=("Inter", 13 * -1)
            )

            image_image_12 = PhotoImage(
                file=relative_to_assets("image_12.png"))
            image_12 = self.canvas.create_image(
                1075.6249389648438,
                192.50003051757812,
                image=image_image_12
            )

            self.canvas.create_text(
                1036.1248779296875,
                174.37496948242188,
                anchor="nw",
                text="Speed",
                fill="#FFFFFF",
                font=("Inter", 12 * -1)
            )

            self.canvas.create_text(
                1028.2498779296875,
                295.8749694824219,
                anchor="nw",
                text="Speed X\n",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
            )

            self.x_speed = self.canvas.create_text(
                1028.2498779296875,
                313.8749694824219,
                anchor="nw",
                text="N/A cm/s",
                fill="#FE8944",
                font=("Inter Bold", 12 * -1)
            )

            self.canvas.create_text(
                1028.2498779296875,
                348.74993896484375,
                anchor="nw",
                text="Speed Y\n",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
            )

            self.canvas.create_text(
                1274.6251220703125,
                295.8749694824219,
                anchor="nw",
                text="Flight Time",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
            )

            self.y_speed = self.canvas.create_text(
                1028.2498779296875,
                366.7499694824219,
                anchor="nw",
                text="N/A cm/s",
                fill="#FE8944",
                font=("Inter Bold", 12 * -1)
            )

            self.canvas.create_text(
                1028.2498779296875,
                400.5,
                anchor="nw",
                text="Speed Z\n",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
            )

            self.z_speed = self.canvas.create_text(
                1028.2498779296875,
                418.49993896484375,
                anchor="nw",
                text="N/A cm/s",
                fill="#FE8944",
                font=("Inter Bold", 12 * -1)
            )

            image_image_13 = PhotoImage(
                file=relative_to_assets("image_13.png"))
            image_13 = self.canvas.create_image(
                1011.6249389648438,
                176.24996948242188,
                image=image_image_13
            )

            self.speed = self.canvas.create_text(
                1036.1248779296875,
                201.37501525878906,
                anchor="nw",
                text="N/A cm/s",
                fill="#FFFFFF",
                font=("Inter", 13 * -1)
            )

            image_image_14 = PhotoImage(
                file=relative_to_assets("image_14.png"))
            image_14 = self.canvas.create_image(
                1011.0000281453018,
                204.6249656677246,
                image=image_image_14
            )

            image_image_15 = PhotoImage(
                file=relative_to_assets("image_15.png"))
            image_15 = self.canvas.create_image(
                1287.3748779296875,
                192.50003051757812,
                image=image_image_15
            )

            image_image_16 = PhotoImage(
                file=relative_to_assets("image_16.png"))
            image_16 = self.canvas.create_image(
                1235.4998779296875,
                178.49996948242188,
                image=image_image_16
            )

            self.canvas.create_text(
                1262.2498779296875,
                174.37496948242188,
                anchor="nw",
                text="Distance to floor",
                fill="#FFFFFF",
                font=("Inter", 12 * -1)
            )

            self.tof = self.canvas.create_text(
                1262.2498779296875,
                201.37501525878906,
                anchor="nw",
                text="N/A cm",
                fill="#FFFFFF",
                font=("Inter", 13 * -1)
            )

            image_image_17 = PhotoImage(
                file=relative_to_assets("image_17.png"))
            image_17 = self.canvas.create_image(
                1234.8749046325684,
                206.8749963330236,
                image=image_image_17
            )

            self.canvas.create_rectangle(
                1118.2498780488968,
                292.5000001192093,
                1119.3748779296875,
                453.37498474121094,
                fill="#FFFFFF",
                outline="")

            self.canvas.create_rectangle(
                1259.9998780488968,
                292.5000001192093,
                1261.1248779296875,
                453.37498474121094,
                fill="#FFFFFF",
                outline="")

            button_image_1 = PhotoImage(
                file=relative_to_assets("button_1.png"))
            button_1 = Button(
                image=button_image_1,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: print("button_1 clicked"),
                relief="flat"
            )
            button_1.place(
                x=634.5,
                y=731.2499389648438,
                width=170.99998474121094,
                height=50.625
            )

            button_image_2 = PhotoImage(
                file=relative_to_assets("button_2.png"))
            button_2 = Button(
                image=button_image_2,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: print("button_2 clicked"),
                relief="flat"
            )
            button_2.place(
                x=634.5,
                y=795.375,
                width=170.99998474121094,
                height=50.625
            )

            button_image_3 = PhotoImage(
                file=relative_to_assets("button_3.png"))
            button_3 = Button(
                image=button_image_3,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: print("button_3 clicked"),
                relief="flat"
            )
            button_3.place(
                x=634.5,
                y=667.1249389648438,
                width=170.99998474121094,
                height=50.625
            )

            self.t_key = self.canvas.create_rectangle(
                559.1249389648438,
                668.2499389648438,
                610.8749351501465,
                717.7499389648438,
                fill="#303133",
                outline="")

            self.l_key = self.canvas.create_rectangle(
                559.1249389648438,
                732.3748779296875,
                610.8749351501465,
                781.8748779296875,
                fill="#303133",
                outline="")

            self.q_key = self.canvas.create_rectangle(
                995.6249389648438,
                640.125,
                1059.7499313354492,
                700.8749961853027,
                fill="#303133",
                outline="")

            self.d_key = self.canvas.create_rectangle(
                1152.0001220703125,
                707.625,
                1216.125114440918,
                768.3749961853027,
                fill="#303133",
                outline="")

            self.s_key = self.canvas.create_rectangle(
                1082.2498779296875,
                707.625,
                1146.374870300293,
                768.3749961853027,
                fill="#303133",
                outline="")

            self.a_key = self.canvas.create_rectangle(
                1012.4999389648438,
                707.625,
                1076.6249313354492,
                768.3749961853027,
                fill="#303133",
                outline="")

            self.e_key = self.canvas.create_rectangle(
                1132.8748779296875,
                640.125,
                1196.999870300293,
                700.8749961853027,
                fill="#303133",
                outline="")

            self.f_key = self.canvas.create_rectangle(
                1231.8748779296875,
                640.125,
                1295.999870300293,
                700.8749961853027,
                fill="#303133",
                outline="")

            self.y_key = self.canvas.create_rectangle(
                1300.4998779296875,
                640.125,
                1364.624870300293,
                700.8749961853027,
                fill="#303133",
                outline="")

            self.g_key = self.canvas.create_rectangle(
                1231.8748779296875,
                707.625,
                1295.999870300293,
                768.3749961853027,
                fill="#303133",
                outline="")

            self.p_key = self.canvas.create_rectangle(
                1263.3751220703125,
                790.8751220703125,
                1327.500114440918,
                851.6251182556152,
                fill="#303133",
                outline="")

            self.r_key = self.canvas.create_rectangle(
                1300.4998779296875,
                707.625,
                1364.624870300293,
                768.3749961853027,
                fill="#303133",
                outline="")

            self.w_key = self.canvas.create_rectangle(
                1064.25,
                640.125,
                1128.3749923706055,
                700.8749961853027,
                fill="#303133",
                outline="")

            image_image_18 = PhotoImage(
                file=relative_to_assets("image_18.png"))
            image_18 = self.canvas.create_image(
                1016.9888302713541,
                301.8749694824219,
                image=image_image_18
            )

            image_image_19 = PhotoImage(
                file=relative_to_assets("image_19.png"))
            image_19 = self.canvas.create_image(
                1010.6249256134033,
                301.87495469796323,
                image=image_image_19
            )

            image_image_20 = PhotoImage(
                file=relative_to_assets("image_20.png"))
            image_20 = self.canvas.create_image(
                1015.875,
                354.37494761395953,
                image=image_image_20
            )

            image_image_21 = PhotoImage(
                file=relative_to_assets("image_21.png"))
            image_21 = self.canvas.create_image(
                1011.3748952279191,
                358.87494680929603,
                image=image_image_21
            )

            image_image_22 = PhotoImage(
                file=relative_to_assets("image_22.png"))
            image_22 = self.canvas.create_image(
                1011.7498165994791,
                403.1249558359293,
                image=image_image_22
            )

            image_image_23 = PhotoImage(
                file=relative_to_assets("image_23.png"))
            image_23 = self.canvas.create_image(
                1011.7499247704894,
                409.48895179380486,
                image=image_image_23
            )

            image_image_24 = PhotoImage(
                file=relative_to_assets("image_24.png"))
            image_24 = self.canvas.create_image(
                1357.1248779296875,
                301.8749694824219,
                image=image_image_24
            )

            self.q_keytext = self.canvas.create_text(
                1018.1249389648438,
                658.1249389648438,
                anchor="nw",
                text="Q",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.a_keytext = self.canvas.create_text(
                1036.1248779296875,
                724.4999389648438,
                anchor="nw",
                text="A",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.s_keytext = self.canvas.create_text(
                1106.9998779296875,
                724.4999389648438,
                anchor="nw",
                text="S",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.d_keytext = self.canvas.create_text(
                1176.7498779296875,
                724.4999389648438,
                anchor="nw",
                text="D",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.w_keytext = self.canvas.create_text(
                1083.375,
                656.9999389648438,
                anchor="nw",
                text="W",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.e_keytext = self.canvas.create_text(
                1157.625,
                656.9999389648438,
                anchor="nw",
                text="E",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.f_keytext = self.canvas.create_text(
                1256.625,
                656.9999389648438,
                anchor="nw",
                text="F",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.g_keytext = self.canvas.create_text(
                1254.3748779296875,
                724.4999389648438,
                anchor="nw",
                text="G",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.y_keytext = self.canvas.create_text(
                1322.9998779296875,
                656.9999389648438,
                anchor="nw",
                text="Y",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.r_keytext = self.canvas.create_text(
                1325.25,
                724.4999389648438,
                anchor="nw",
                text="R",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.p_keytext = self.canvas.create_text(
                1288.125,
                807.7499389648438,
                anchor="nw",
                text="P",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.t_keytext = self.canvas.create_text(
                577.125,
                678.375,
                anchor="nw",
                text="T",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            self.l_keytext = self.canvas.create_text(
                577.125,
                742.4998779296875,
                anchor="nw",
                text="L",
                fill="#373B3C",
                font=("Inter Bold", 24 * -1)
            )

            image_image_25 = PhotoImage(
                file=relative_to_assets("image_25.png"))
            image_25 = self.canvas.create_image(
                1357.1248779296875,
                354.74993896484375,
                image=image_image_25
            )

            image_image_26 = PhotoImage(
                file=relative_to_assets("image_26.png"))
            image_26 = self.canvas.create_image(
                1357.1248779296875,
                406.5,
                image=image_image_26
            )

            # Key dict
            self.key_dict = {'w': self.w_key, 
                             'a': self.a_key, 
                             's': self.s_key, 
                             'd': self.d_key, 
                             'q': self.q_key, 
                             'e': self.e_key, 
                             'f': self.f_key, 
                             'g': self.g_key, 
                             'y': self.y_key, 
                             'r': self.r_key, 
                             'p': self.p_key, 
                             't': self.t_key, 
                             'l': self.l_key}
            self.key_text_dict = {'w': self.w_keytext,
                                  'a': self.a_keytext,
                                  's': self.s_keytext,
                                  'd': self.d_keytext,
                                  'q': self.q_keytext,
                                  'e': self.e_keytext,
                                  'f': self.f_keytext,
                                  'g': self.g_keytext,
                                  'y': self.y_keytext,
                                  'r': self.r_keytext,
                                  'p': self.p_keytext,
                                  't': self.t_keytext,
                                  'l': self.l_keytext}
            # Colour w key
            self.input_frame.bind('<KeyPress-w>', lambda e: self.update_object(True, 'w'))
            self.input_frame.bind('<KeyRelease-w>', lambda e: self.update_object(False, 'w'))

            # Colour a key
            self.input_frame.bind('<KeyPress-a>', lambda e: self.update_object(True, 'a'))
            self.input_frame.bind('<KeyRelease-a>', lambda e: self.update_object(False, 'a'))

            # Colour s key
            self.input_frame.bind('<KeyPress-s>', lambda e: self.update_object(True, 's'))
            self.input_frame.bind('<KeyRelease-s>', lambda e: self.update_object(False, 's'))

            # Colour d key
            self.input_frame.bind('<KeyPress-d>', lambda e: self.update_object(True, 'd'))
            self.input_frame.bind('<KeyRelease-d>', lambda e: self.update_object(False, 'd'))

            # Colour q key
            self.input_frame.bind('<KeyPress-q>', lambda e: self.update_object(True, 'q'))
            self.input_frame.bind('<KeyRelease-q>', lambda e: self.update_object(False, 'q'))

            # Colour e key
            self.input_frame.bind('<KeyPress-e>', lambda e: self.update_object(True, 'e'))
            self.input_frame.bind('<KeyRelease-e>', lambda e: self.update_object(False, 'e'))

            # Colour f key
            self.input_frame.bind('<KeyPress-f>', lambda e: self.update_object(True, 'f'))
            self.input_frame.bind('<KeyRelease-f>', lambda e: self.update_object(False, 'f'))

            # Colour g key
            self.input_frame.bind('<KeyPress-g>', lambda e: self.update_object(True, 'g'))
            self.input_frame.bind('<KeyRelease-g>', lambda e: self.update_object(False, 'g'))

            # Colour y key
            self.input_frame.bind('<KeyPress-y>', lambda e: self.update_object(True, 'y'))
            self.input_frame.bind('<KeyRelease-y>', lambda e: self.update_object(False, 'y'))

            # Colour r key
            self.input_frame.bind('<KeyPress-r>', lambda e: self.update_object(True, 'r'))
            self.input_frame.bind('<KeyRelease-r>', lambda e: self.update_object(False, 'r'))

            # Colour p key
            self.input_frame.bind('<KeyPress-p>', lambda e: self.update_object(True, 'p'))
            self.input_frame.bind('<KeyRelease-p>', lambda e: self.update_object(False, 'p'))

            # Colour t key
            self.input_frame.bind('<KeyPress-t>', lambda e: self.update_object(True, 't'))
            self.input_frame.bind('<KeyRelease-t>', lambda e: self.update_object(False, 't'))

            # Colour l key
            self.input_frame.bind('<KeyPress-l>', lambda e: self.update_object(True, 'l'))
            self.input_frame.bind('<KeyRelease-l>', lambda e: self.update_object(False, 'l'))

            self.input_frame.bind()
            # Pack the input frame
            self.input_frame.pack()
            self.input_frame.focus_set()


            self.update_stats()
            self.video_loop()

            threading.Thread(target=lambda: self.keyboard_thread.run(), daemon=True).start()

            self.window.mainloop()
        except Exception as e:
            print(f"Error running app: {e}")
        finally:
            self.cleanup()

    # Updating key colour to show what is being pressed
    def update_object(self, update, char):
        
        if update == False:
            self.canvas.itemconfig(self.key_dict[char], fill="#303133")
            self.canvas.itemconfig(self.key_text_dict[char], fill="#373B3C")
        else:
            self.canvas.itemconfig(self.key_dict[char], fill="#FE8944")
            self.canvas.itemconfig(self.key_text_dict[char], fill="#FFFFFF")
            if char == 'p':
                frame = self.frame.frame
                self.image_queue.put((frame, self.drone.get_flight_time(), datetime.now()))
                print(frame)

    def video_loop(self):
        """
        The video loop is used to continuously get the current frame
        from the drone and display it in the GUI
        """
        detection_centers = []
        # Define the height and width to resize the current frame to
        h = 540
        w = 810

        # Read a frame from our drone
        frame = self.frame.frame

        frame = cv2.resize(frame, (w, h))
       
        
        # Convert the current frame to the rgb colorspace
        cv2image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2image = cv2image[:, :, ::-1].copy()
        if not self.enable_cv_queue.empty():
            print("Computer Vision Enabled/Disabled!")
            self.detect = not self.detect
            self.enable_cv_queue.get()
        if self.detect:
            detections = model(cv2image)[0] # what is detected in the frame
            for detect in detections.boxes.data.tolist():
                confidence = detect[4] 
                # If the confidence of the model is below 30%, skip it
                if float(confidence) < .2: 
                    continue
                xmin, ymin, xmax, ymax = int(detect[0]), int(detect[1]), int(detect[2]), int(detect[3])
                # Creating a bounding box
                bounding_box = cv2.rectangle(cv2image, 
                                            (xmin, ymin), 
                                            (xmax, ymax), 
                                            (255, 0, 0), 
                                            2) 
                detection_centers.append((xmax/2, ymax/2))
                # This code simply adds text to the box.
                cv2.putText(bounding_box, 
                            names[detect[5]], 
                            (xmin, ymin-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.6, 
                            (36,255,12), 
                            2)
        # Convert this to a Pillow Image object
        img = Image.fromarray(cv2image)

        # Convert this then to a Tkinter compatible PhotoImage object
        self.imgtk = ImageTk.PhotoImage(image=img)

        # Configure the photo image as the displayed image
        self.canvas.itemconfig(self.video_image, image=self.imgtk)
        self.canvas.update()

        # Update the video loop after 33ms, or 30fps
        self.canvas.after(33, self.video_loop)

    def update_stats(self):

        """
        Call the get_current_state method from the drone object
        to get all of the statistics from one call
        This is done to reduce the amount of calls to the drone
        and to reduce the amount of time it takes to get the data
        """

        state = self.drone.get_current_state()
        self.canvas.itemconfig(self.rolltext, text=f"{state['roll']}°")
        self.canvas.itemconfig(self.pitch_text, text=f"{state['pitch']}°")
        self.canvas.itemconfig(self.yaw_text, text=f"{state['yaw']}°")
        self.canvas.itemconfig(self.height, text=f"{state['h']} cm")
        self.canvas.itemconfig(self.barometer, text=f"{state['baro']} cm")
        self.canvas.itemconfig(self.temperature, text=f"{round(state['templ'] + state['temph']) / 2}° C")
        self.canvas.itemconfig(self.battery_text, text=f"{state['bat']}%")
        self.canvas.itemconfig(self.battery_mah, text=f"{(state['bat'] / 100) * 1100} / 1100 mAh")
        self.canvas.itemconfig(self.speed, text=f"{self.drone.speed} cm/s")
        self.canvas.itemconfig(self.x_speed, text=f"{state['vgx']} cm/s")
        self.canvas.itemconfig(self.y_speed, text=f"{state['vgy']} cm/s")
        self.canvas.itemconfig(self.z_speed, text=f"{state['vgz']} cm/s")
        self.canvas.itemconfig(self.tof, text=f"{state['tof']} cm")
        self.canvas.itemconfig(self.flight_time, text=f"{state['time']} s")

        # Update after 33ms, or 30fps
        self.window.after(33, self.update_stats)

    def cleanup(self) -> None:
        try:
            print("Closing interface.")
            if self.drone.is_flying: self.drone.land()
            self.drone.end()
            self.window.quit()
            if not self.image_queue.empty():
                print("Queue isn't empty")
                image_array = []
                while not self.image_queue.empty():
                    image = self.image_queue.get()
                    image_array.append(image)
                create_report(image_array)
            self.keyboard_thread.terminate()
            exit()
        except Exception as e:
            print(f"Error performing cleanup: {e}")

if __name__ == "__main__":
    gui = DroneGUI()
    gui.run_app()