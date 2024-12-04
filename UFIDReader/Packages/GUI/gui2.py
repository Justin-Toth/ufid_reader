import customtkinter
import os
# from dotenv import load_dotenv
from PIL import Image, ImageTk
import time
import threading
import logging
from src.main import process_scan

# NOTE: This GUI relies on being used in the context of the main.py file in the src folder (cannot be run standalone)

# commented out for now to simplify but can use .env file for environment variables instead of storeing paths in code
# Load environment variables from .env file
# load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.env"))

# Read environment variables
# ENABLE_LOGGING = os.getenv("ENABLE_LOGGING") == "true"

ENABLE_LOGGING = True

# Path to the images directory
image_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images'))

# Setup Logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../Logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "gui.log")

logger = logging.getLogger("gui_logger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="[%Y-%m-%d %H:%M:%S]")

file_handler = logging.FileHandler(LOG_FILE, mode='w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

if ENABLE_LOGGING:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


class App2(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Setup the main window and UI components
        self.setup_window()
        self.setup_fonts_and_sizes()
        self.setup_frames()
        self.bind_all("<Key>", self.capture_scan)

    # Seting up the main window properties
    def setup_window(self):
        # Gets current display's width and height
        # screen_width = self.winfo_screenwidth()
        # screen_height = self.winfo_screenheight()
        
        # Static sets for now
        screen_width = 1080
        screen_height = 720
        
        self.geometry(f"{screen_width}x{screen_height}")
        self.scanner_input = ""
        self.prev_scan = ""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        logger.info("Window setup complete with dimensions: %dx%d", screen_width, screen_height)

    # Setup dynamic font sizes and image sizes based on screen height
    def setup_fonts_and_sizes(self):
        screen_height = self.winfo_screenheight()
        self.font_size_information = max(16, int(screen_height * 0.04))
        self.font_size_prompt = max(16, int(screen_height * 0.1))
        self.font_size_result = max(16, int(screen_height * 0.04))
        self.font_size_loading = max(16, int(screen_height * 0.06))
        self.prompt_image_size = int(screen_height * 0.3)
        self.result_image_size = int(screen_height * 0.5)
        self.spinner_gif_size = int(screen_height * 0.3)
        self.gator_logo_size = int(screen_height * 0.25)
        logger.info("Font sizes and image sizes setup complete")

    # Initialize all the frames used in the application
    def setup_frames(self):
        self.information_frame_init()
        self.scan_frame_init()
        self.success_frame_init()
        self.fail_frame_init()
        logger.info("Frames setup complete \n")

    # Initialize the information frame
    def information_frame_init(self):
        self.information_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.information_frame.grid(row=0, column=0, sticky="nsew")

        self.information_frame.grid_rowconfigure(0, weight=1)
        self.information_frame_title_top = customtkinter.CTkLabel(
            self.information_frame,
            text=" UFID Check-In \n System ",
            compound="left",
            font=customtkinter.CTkFont(size=self.font_size_information, weight="bold")
        )
        self.information_frame_title_top.grid(row=0, column=0, padx=0, pady=int(self.winfo_screenheight() * 0.05), sticky="new")

        self.information_frame_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_dir_path, "gators_logo.png")),
            size=(self.gator_logo_size, self.gator_logo_size * (2 / 3))
        )
        self.information_frame_image_label = customtkinter.CTkLabel(
            self.information_frame,
            text="",
            compound="left",
            image=self.information_frame_image,
            font=customtkinter.CTkFont(size=self.font_size_information, weight="bold")
        )
        self.information_frame_image_label.place(anchor="c", relx=0.5, rely=0.3)

        self.invisible_text_box = customtkinter.CTkEntry(
            self.information_frame,
            font=customtkinter.CTkFont(size=self.font_size_information, weight="bold"),
            fg_color="transparent",
            border_width=0,
            text_color="black",
            justify="center",
        )
        self.invisible_text_box.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, int(self.winfo_screenheight() * 0.05)))

        self.exit_button = customtkinter.CTkButton(
            self.information_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text="",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=lambda: self.destroy()
        )
        self.exit_button.grid(row=2, column=0, sticky="ew")

        self.information_frame_time = customtkinter.CTkLabel(
            self.information_frame,
            text="",
            compound="left",
            font=customtkinter.CTkFont(size=max(16, self.font_size_information - 10), weight="bold")
        )
        self.information_frame_time.grid(row=3, column=0, padx=0, pady=(0, int(self.winfo_screenheight() * 0.05)), sticky="sew")
        self.update_time()
        logger.info("Information frame initialized")

    # Initialize the scan frame
    def scan_frame_init(self):
        self.scan_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="white", bg_color="white")
        self.scan_frame.grid_columnconfigure(0, weight=1)

        self.prompt_label = customtkinter.CTkLabel(
            self.scan_frame,
            text=" Swipe UFID or \n tap below",
            font=customtkinter.CTkFont("Roboto", size=self.font_size_prompt),
            anchor="center",
            text_color="black"
        )
        self.prompt_label.grid(padx=0, pady=(int(self.winfo_screenheight() * 0.1), int(self.winfo_screenheight() * 0.01)))

        img = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_dir_path, "arrow.png")),
            size=(self.prompt_image_size, self.prompt_image_size)
        )
        self.img_label = customtkinter.CTkLabel(self.scan_frame, text='', image=img)
        self.img_label.grid(padx=0, pady=int(self.winfo_screenheight() * 0.01))
        logger.info("Scan frame initialized")

    # Initialize the success frame
    def success_frame_init(self):
        self.success_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="white", bg_color="white")
        self.success_frame.grid_rowconfigure(0, weight=1)
        self.success_frame.grid_columnconfigure(1, weight=1)

        self.success_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_dir_path, "checkmark.png")),
            size=(self.result_image_size, self.result_image_size)
        )
        self.success_image_label = customtkinter.CTkLabel(self.success_frame, text="", image=self.success_image)
        self.success_image_label.place(anchor="c", relx=0.5, rely=0.40)

        self.success_text_label = customtkinter.CTkLabel(
            self.success_frame,
            text="",
            text_color="black",
            font=("Roboto", self.font_size_result)
        )
        self.success_text_label.place(anchor="c", relx=0.5, rely=0.75)
        logger.info("Success frame initialized")

    # Initialize the fail frame
    def fail_frame_init(self):
        self.fail_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="white", bg_color="white")
        self.fail_frame.grid_rowconfigure(0, weight=1)
        self.fail_frame.grid_columnconfigure(1, weight=1)

        self.fail_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_dir_path, "incorrect.png")),
            size=(self.result_image_size, self.result_image_size)
        )
        self.fail_image_label = customtkinter.CTkLabel(self.fail_frame, text='', image=self.fail_image)
        self.fail_image_label.place(anchor="c", relx=0.5, rely=0.40)

        self.fail_text_label = customtkinter.CTkLabel(
            self.fail_frame,
            text="",
            text_color="black",
            font=("Roboto", self.font_size_result)
        )
        self.fail_text_label.place(anchor="c", relx=0.5, rely=0.75)
        logger.info("Fail frame initialized")

    # Update the current date and time every second
    def update_time(self):
        current_date = time.strftime("%d %b %Y")
        current_time = time.strftime("%I:%M:%S").lstrip('0')
        self.information_frame_time.configure(text=f" {current_date} \n {current_time} ")
        self.after(1000, self.update_time)

    # Select and display the appropriate frame based on the name
    def select_frame_by_name(self, name, student_info):
        self.scan_frame.grid_remove()
        self.success_frame.grid_remove()
        self.fail_frame.grid_remove()

        if name == "scan":
            self.scan_frame.grid(row=0, column=1, sticky="nsew")
            logger.info("Displaying scan frame")
        elif name == "success":
            output = f"{student_info['First Name']} {student_info['Last Name']} has been validated successfully."
            self.success_text_label.configure(text=output)
            self.success_frame.grid(row=0, column=1, sticky="nsew")
            logger.info("Displaying success frame with message: %s", output)
            self.after(2000, lambda: self.select_frame_by_name("scan", student_info=None))  # 2 seconds
        elif name == "fail":
            output = self.get_fail_message(student_info["Valid"])
            self.fail_text_label.configure(text=output)
            self.fail_frame.grid(row=0, column=1, sticky="nsew")
            logger.info("Displaying fail frame with message: %s", output)
            self.after(3000, lambda: self.select_frame_by_name("scan", student_info=None))  # 3 seconds

    # Get the failure message based on the validation code
    def get_fail_message(self, valid_code):
        messages = {
            -1: "Serial Number not found.",
            -2: "UFID not found. Please use the form provided by your\nprofessor to add yourself to the system.",
            -3: "Incorrect time. Please scan during your class period.",
            -4: "Please scan during a school day.",
        }
        message = messages.get(valid_code, "Unknown Error: Please see IT for assistance.")
        logger.info("Failure message: %s", message)
        return message

    # Capture the scan input and process it
    def capture_scan(self, event):
        self.scanner_input += event.char
        if event.keysym == "Return":
            logger.info("Scan captured: %s", self.scanner_input.strip())
            process_scan(self)
            self.invisible_text_box.delete(0, 'end')
            logger.info("Scan processed and input box cleared \n")

if __name__ == "__main__":
    app = App2()
    app.mainloop()