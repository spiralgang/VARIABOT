import time
import subprocess
import os

LOG_FILE = "/sdcard/root_adapt.log"

def get_last_error():
    if not os.path.exists(LOG_FILE):
        return None
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()
        for line in reversed(lines):
            if 'error' in line.lower():
                return line
    return None

def mutate_script():
    # This is a placeholder for a more sophisticated mutation engine.
    # In a real scenario, this would involve more complex logic to determine the best mutation.
    with open('/home/serverhustled/VARIABOT/android_rooting/scripts/finalize_root.sh', 'a') as f:
        f.write('\necho "Mutation: Retrying with SELinux permissive..." >> /sdcard/root_adapt.log')
        f.write('\nsetenforce 0')

def run_script():
    subprocess.run(['/home/serverhustled/VARIABOT/android_rooting/scripts/finalize_root.sh'], check=False)

if __name__ == "__main__":
    while True:
        last_error = get_last_error()
        if last_error:
            print(f"Error detected: {last_error}")
            print("Mutating script and retrying...")
            mutate_script()
            run_script()
        else:
            print("No errors detected. Rooting process appears successful.")
            break
        time.sleep(5)