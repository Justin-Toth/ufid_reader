import sys
import time
import os
import signal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Packages.Validation import *
from Packages.GUI import *

# Global variable to keep track of the mode
mode = 1

# Process the scan input and validate the student
def process_scan(self):
    # Temp code to allow for switching between modes
    global mode

    # Note: we will need to eventually add retreival of the serial number for the kiosk check from the pi
    start_time = time.time()
    scanner_input = self.scanner_input.strip()
    
    if scanner_input == "exit":
        print("Exiting Program")
        sys.exit(0)
    elif len(scanner_input) == 16:
        valid = validate(mode, "10000000d340eb60", card_iso=scanner_input)
    else:
        valid = validate(mode, "10000000d340eb60", card_ufid=scanner_input)

    end_time = time.time()
    time_total = end_time - start_time
    print(f"Total Time to run validation: {time_total} \n")

    display_result(self, valid)

    # Toggle the mode for the next call
    mode = 1 if mode == 0 else 0

    # Reset scanner_input for new scan
    self.scanner_input = ""

def display_result(self, valid):
    if valid["Valid"] == 0:
        self.select_frame_by_name("success", student_info=valid)
    else:
        self.select_frame_by_name("fail", student_info=valid)

def gui_main_loop():
    app = App()
    app.select_frame_by_name("scan", student_info=None)
    app.mainloop()

if __name__ == "__main__":
    gui_main_loop()
