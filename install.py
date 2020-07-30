import subprocess

if __name__ == "__main__":
    subprocess.call(f"pip install .[dev]", shell=True)
    subprocess.call(f"pip install ./mapyastar ", shell=True)
