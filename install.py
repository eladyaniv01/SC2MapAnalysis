import os
import subprocess

if __name__ == "__main__":
    subprocess.call(f"pip install {os.path.join(os.getcwd(), 'mapyastar')}. -v", shell=True)
    # subprocess.call(f"pip install .", shell=True)
    # subprocess.call(f"pip install {os.path.join(os.getcwd(), 'mapyastar')}", shell=True)
