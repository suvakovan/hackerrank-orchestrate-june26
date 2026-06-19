import shutil
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.join(BASE_DIR, "code")
ZIP_NAME = os.path.join(BASE_DIR, "submission")

print(f"Zipping the {CODE_DIR} directory...")

# Create a zip file of the code directory
shutil.make_archive(ZIP_NAME, 'zip', CODE_DIR)

print(f"Successfully created {ZIP_NAME}.zip!")
print("Make sure to include evaluation_report.md and output.csv in your final upload if required by the platform.")
