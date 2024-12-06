import concurrent.futures
import os
import random
import logging
import time

from ufid_reader.UFIDReader.Packages.Validation.validation import validate 

# Enable/Disable logging
ENABLE_LOGGING = True

# Setup Logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../Logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "stress_test.log")

stress_test_logger = logging.getLogger("stress_test_logger")
stress_test_logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]"
)

file_handler = logging.FileHandler(LOG_FILE, mode='w')
file_handler.setFormatter(formatter)
stress_test_logger.addHandler(file_handler)

if ENABLE_LOGGING:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stress_test_logger.addHandler(stream_handler)


def stress_test_instance(instance_id):
    """
    A single instance of the validation process for stress testing.
    Args:
        instance_id (int): The ID of the test instance for logging.
    Returns:
        dict: Result of the validation call.
    """
    log_messages = []
    
    try:
        mode = random.choice([0, 1])  # Randomly pick a mode
        serial_num = "10000000d340eb60"  # Generate a unique serial number from the list of valid kiosks (currently using the NSC215 kiosk)
        card_ufid = 91547610  # Generate a random UFID (currently using mine for testing because I don't have testing data in the db)
        card_iso = None  # You can replace this with test data if needed
        
        log_messages.append(f"Instance {instance_id}: Starting validation with mode {mode}, serial_num {serial_num}, card_ufid {card_ufid}.")
        
        start_time = time.time()
        result = validate(mode=mode, serial_num=serial_num, card_ufid=card_ufid, card_iso=card_iso)
        end_time = time.time()
        
        log_messages.append(f"Instance {instance_id}: Result: Valid={result.get('Valid')}.")
        elapsed_time = end_time - start_time
        log_messages.append(f"Instance {instance_id}: Completed in {elapsed_time:.2f} seconds. \n")
    except Exception as e:
        log_messages.append(f"Instance {instance_id}: Exception occurred: {e}. \n")
        result = {"error": str(e)}
    
    for message in log_messages:
        stress_test_logger.info(message)
    
    return result

def stress_test(num_instances, max_workers):
    """
    Runs multiple instances of the validation script in parallel.
    Args:
        num_instances (int): Total number of validation calls to make.
        max_workers (int): Number of concurrent workers (threads).
    """
    stress_test_logger.info(f"Starting stress test with {num_instances} instances and {max_workers} workers.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(stress_test_instance, i) for i in range(num_instances)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    stress_test_logger.info(f"Stress test completed. Total instances: {len(results)}.")
    return results


# NOTE: This script is meant to be run as a standalone script for testing purposes.
#       Running this script will make the validation.log difficult to parse due to the parallel logging.
if __name__ == "__main__":
    try:
        NUM_INSTANCES = int(input("Enter the total number of validation calls: "))
        MAX_WORKERS = int(input("Enter the number of parallel threads to use: "))
    except ValueError:
        print("Please enter valid integer values.")
        exit(1)

    # Run the stress test
    stress_test_results = stress_test(NUM_INSTANCES, MAX_WORKERS)

    # Output summary
    valid_count = sum(1 for result in stress_test_results if result.get("Valid") == 0)
    stress_test_logger.info(f"Validation Summary: {valid_count}/{NUM_INSTANCES} validations were successful.")
