import os
import subprocess
import sys

venv_dir = '.venv'

# Check if the virtual environment directory exists
if not os.path.exists(venv_dir):
    # Create the virtual environment
    subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
    print(f'Virtual environment created at {venv_dir}')

# Activate the virtual environment and install dependencies
if os.name == 'nt':
    activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')
else:
    activate_script = os.path.join(venv_dir, 'bin', 'activate')

# Install dependencies from requirements.txt
subprocess.run([activate_script, '&&', 'pip', 'install', '-r', 'requirements.txt'], shell=True, check=True)
print('Dependencies installed')