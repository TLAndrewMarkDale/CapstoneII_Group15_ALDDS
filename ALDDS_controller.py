from pynput import keyboard
import os
import queue
import time
import threading
from datetime import datetime


# Class for controlling the drone via keyboard commands
class KeyboardController:
    def __init__(self, flip_cv, drone=None):
        self.boolean_lock = threading.Lock()
        self.movement_reset = []
        self.drone = drone
        self.flip = flip_cv
        if self.drone is not None:
            self.drone.speed = 50

    # Method to handle key press events
    def on_press(self, key):
        lr, fb, ud, yv = 0, 0, 0, 0
        start = time.perf_counter()
        try:
            if key == keyboard.Key.esc:
                if self.drone is not None:
                    self.drone.land()
                os._exit(0)
            elif key.char == 'w':
                print('forward')
                fb = self.drone.speed
            elif key.char == 's':
                print('backward')
                fb = -self.drone.speed
            elif key.char == 'a':
                print('left')
                lr = -self.drone.speed
            elif key.char == 'd':
                print('right')
                lr = self.drone.speed
            elif key.char == 'q':
                print('rotate left')
                yv = -self.drone.speed
            elif key.char == 'e':
                print('rotate right')
                yv = self.drone.speed
            elif key.char == 'f':
                print('up')
                ud = self.drone.speed
            elif key.char == 'g':
                print('down')
                ud = -self.drone.speed
            elif key.char == 't':
                print('takeoff')
                if self.drone is not None and not self.drone.is_flying:
                    threading.Thread(target=lambda: self.drone.takeoff()).start()
            elif key.char == 'l':
                print('land')
                if self.drone is not None and self.drone.is_flying:
                    threading.Thread(target=lambda: self.drone.land()).start()
            
            elif key.char == 'y':
                try:
                    if self.flip is None:
                        print("Error with flip_cv")
                    if self.flip is not None:
                        self.flip.put("flip")
                except Exception as e:
                    print(e)
                print('y pressed')
            elif key.char == 'r':
                threading.Thread(target=lambda: self.reverse(self.movement_reset)).start()
            if self.drone is not None and [lr, fb, ud, yv] != [0, 0, 0, 0]:
                end_time = time.perf_counter() - start
                self.movement_reset.append((lr, fb, ud, yv, end_time))
                threading.Thread(target=lambda: self.movement([lr, fb, ud, yv])).start()
                
        except AttributeError:
            pass
            
    # Method to send movement commands to the drone
    def movement(self, movement):
        if self.drone is not None:
            self.drone.send_rc_control(movement[0], movement[1], movement[2], movement[3])
            time.sleep(0.05)

    # Method to reverse the movements of the drone
    def reverse(self, movement_array):
        if self.drone is not None:
            self.drone.rotate_clockwise(180)
            time.sleep(3)
            reverse_order = movement_array[::-1]
            for movement in reverse_order:
                print("reversing movement")
                self.drone.send_rc_control(movement[0], movement[1], -movement[2], movement[3])
                time.sleep(movement[4])
                self.drone.send_rc_control(0,0,0,0)
                time.sleep(0.05)
            self.movement_reset = []

    # Method to handle key release events, stopping the drone
    def on_release(self, key):
        if self.drone is not None:
            self.drone.send_rc_control(0, 0, 0, 0)
    
    # Method to run the keyboard listener
    def run(self):
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            listener.join()
    def terminate(self):
        exit()

if __name__ == '__main__':
    kb = KeyboardController()
    kb.run()
