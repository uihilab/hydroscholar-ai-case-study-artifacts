import subprocess
import sys

packages = [
    "numpy",
    "pandas",
    "requests",
    "tensorflow",
    "scikit-learn",
    "hydrostats"
]

subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)