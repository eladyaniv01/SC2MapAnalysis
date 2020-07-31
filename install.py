import subprocess

if __name__ == "__main__":
    subprocess.call(f"pip install .", shell=True)
    subprocess.call(f"pip install ./mapyastar ", shell=True)
