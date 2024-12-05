import os
import requests
import logging

from dotenv import load_dotenv
from datetime import datetime, timedelta

# commented out for now to simplify but can use .env file for environment variables instead of storeing paths in code
# Load environment variables from .env file
# load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.env"))

# Read environment variables
# ENABLE_LOGGING = os.getenv("ENABLE_LOGGING") == "true"
# BASE_URL = os.getenv("BASE_URL")
# CHECKIN_SITE_URL = os.getenv("CHECKIN_SITE_URL")

ENABLE_LOGGING = True
BASE_URL = "https://gatorufid.pythonanywhere.com/"
CHECKIN_SITE_URL = "https://brirod2240.pythonanywhere.com/api/add_timesheet"

# Setup Logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../Logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "validation.log")

validation_logger = logging.getLogger("validation_logger")
validation_logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="[%Y-%m-%d %H:%M:%S]")

file_handler = logging.FileHandler(LOG_FILE, mode='w')
file_handler.setFormatter(formatter)
validation_logger.addHandler(file_handler)

if ENABLE_LOGGING:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    validation_logger.addHandler(stream_handler)

# Helper function to make GET requests to the API
def web_api_get_request(page, params):    
    url = BASE_URL + page
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        validation_logger.error(f"API error: {e}\n")
        return f"API error: {e}"

# Validates a swiped card for exams or courses
def validate(mode, serial_num, card_iso=None, card_ufid=None):
    log_messages = []
    log_messages.append(f"Starting validation with mode: {mode}, kiosk serial_num: {serial_num}, card_iso: {card_iso}, card_ufid: {card_ufid}")
    
    # Prepare parameters for the API request
    params = {
        "serial_num": serial_num, 
        "iso": card_iso, 
        "ufid": card_ufid
    }

    # Fetch student data
    student_response = web_api_get_request(page="roster", params=params)
    if not student_response or student_response.status_code != 200:
        error_message = student_response.json().get("error", "Unknown error") if student_response else "API unavailable"
        log_messages.append(f"Failed to fetch student data: {error_message} \n")
        error_codes = {
            "Serial number not found": -1,  # -1 indicates invalid serial number
            "UFID or ISO not found": -2  # -2 indicates invalid UFID or ISO
        }
        for message in log_messages:
            validation_logger.info(message)
        return {
            "UFID": None,
            "First Name": None,
            "Last Name": None,
            "Valid": error_codes.get(error_message, -5)  # -5 indicates unknown error
        }

    # Extract student data
    student = student_response.json()
    log_messages.append(f"Student data: {student}")
    
    # Extract student section numbers
    student_sec_nums = [num for num in student["student_data"][4:12] if num]

    # Extract UFID, ISO, and name 
    ufid = student["student_data"][0]
    iso = student["student_data"][1]
    first_name = student["student_data"][2]
    last_name = student["student_data"][3]

    # Get the room number from the kiosks
    room_response = web_api_get_request(page="kiosks", params={"serial_num": serial_num})
    if not room_response or room_response.status_code != 200:
        log_messages.append("Failed to fetch room data. \n")
        for message in log_messages:
            validation_logger.info(message)
        return {
            "UFID": None,
            "First Name": None,
            "Last Name": None,
            "Valid": -5  # -5 indicates unknown error
        }
    room = room_response.json().get("room_num")
    log_messages.append(f"Room: {room}")

    # Determine current day and time
    now = datetime.now()
    date = now.strftime("%m/%d/%Y")
    day_map = {0: "M", 1: "T", 2: "W", 3: "R", 4: "F", 5: "S"}
    day = day_map.get(now.weekday(), None)
    if not day:
        log_messages.append("Invalid school day (e.g., Sunday). \n")
        for message in log_messages:
            validation_logger.info(message)
        return {
            "UFID": None,
            "First Name": None,
            "Last Name": None,
            "Valid": -4  # -4: Invalid school day
        }
    log_messages.append(f"Day: {now.strftime('%A')}")
    current_time = now.time()

    # Create the parameters for the API request based on mode
    params_mode0 = {
        "day": day,
        "roomCode": room
    }
    params_mode1 = {
        "serial_num": serial_num,
        "date": date
    }
    params_data = params_mode1 if mode == 1 else params_mode0       
    endpoint = "exams" if mode == 1 else "courses"
   
    # Fetch course or exam data 
    schedule_response = web_api_get_request(page=endpoint, params=params_data)
    if not schedule_response or schedule_response.status_code != 200:
        log_messages.append("Failed to fetch schedule data. \n")
        for message in log_messages:
            validation_logger.info(message)
        return {
            "UFID": None,
            "First Name": None,
            "Last Name": None,
            "Valid": -5
        }

    results = schedule_response.json()
    log_messages.append(f"Schedule results: {results}")

    # Validate against the schedule
    is_valid = -3  # Default: No match found
    courses = []
    grace_period = timedelta(minutes=15)  # configurable period for class check-in

    for result in results:
        if mode == 1:
            start = datetime.strptime(result[6], '%I:%M %p').replace(year=now.year, month=now.month, day=now.day) 
            end = datetime.strptime(result[7], '%I:%M %p').replace(year=now.year, month=now.month, day=now.day)
        else:
            start = datetime.strptime(result[6], '%I:%M %p').replace(year=now.year, month=now.month, day=now.day) - grace_period
            end = datetime.strptime(result[7], '%I:%M %p').replace(year=now.year, month=now.month, day=now.day) + grace_period
        if start.time() <= current_time <= end.time():
            courses.append(result)

    log_messages.append(f"Matching courses: {courses}")

    # Check student sections against the course schedule
    match_found = False
    for course in courses:
        course_sec_nums = course[3].split(', ') if mode == 1 else course[2]
        for student_sec_num in student_sec_nums:
            if student_sec_num in course_sec_nums:
                log_messages.append(f"Matching courses: {course}")
                
                params = {
                    'serial_num': serial_num,
                    'ufid': ufid,
                    'iso': iso,
                    'first_name': first_name,
                    'last_name': last_name,
                    'course': course[0],
                    'class': student_sec_num,
                    'time': now.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                if mode == 1:
                    params["instructor"] = course[2]
                    params["room_num"] = course[4]
                else:
                    params["instructor"] = course[3]
                    params["room_num"] = course[8]
                
                # Get the timesheet response
                response = requests.post(f"{BASE_URL}timesheet", params=params)
                log_messages.append(f"Timesheet POST response: {response.status_code}, {response.text}")

                # Get the check-in site response
                checkin_site_response = requests.post(CHECKIN_SITE_URL, json=params)
                log_messages.append(f"Check-in site POST response: {checkin_site_response.status_code}, {checkin_site_response.text}")

                is_valid = 0
                match_found = True
                break
            
        if match_found:
            break

    if not match_found:
        log_messages.append("No matching course found for the student. \n")
        is_valid = -5  # unknown error for now

    for message in log_messages:
        validation_logger.info(message)

    return {
        "UFID": ufid,
        "First Name": first_name,
        "Last Name": last_name,
        "Valid": is_valid
    }

# Example call
# validate(mode={0 or 1}, serial_num={serial number from kiosk table}, card_iso={UFID ISO}, cardufid={UFID Number})
# validate(0, serial_num="10000000d340eb60", card_ufid="91547610")
# validate(1, serial_num="10000000d340eb60", card_ufid="91547610")