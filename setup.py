# This script should NOT BE EXECUTED DIRECTLY
# use "python setup.py build" instead (this is how you correctly invoke cx_freeze)

import os
import shutil
import zipfile
import time
import re
import cx_Freeze

if os.path.isdir("build"):
    shutil.rmtree("build")

# Apparently importing the actual script that is built is bad practice and may cause issues
ver = None
with open("blessgen.py", "r") as f:
    for line in f:
        m = re.match('ver = "(.*)"', line)
        if m is not None:
            ver = m.groups()[0]
            print(f"Found version: {ver}")
            break

if ver is None:
    raise Exception("Failed to find version")

build_exe_options = {"include_msvcr": False, "excludes": ["distutils", "test"]}

cx_Freeze.setup(name="BlessGen", version=ver,
                description="BlessGen: A random bless effect generator for Dominions 5",
                options={"build_exe": build_exe_options},
                executables=[cx_Freeze.Executable("blessgen.py")])

# Permissions.
time.sleep(5)

buildfilename = os.listdir("build")[0]
os.rename(f"build/{buildfilename}", f"build/blessgen-{ver}")

# cx_Freeze tries to include a bunch of dlls that Windows users may not have permissions to distribute
# but should be present on any recent system (and available through the MS VC redistributables if not)
# therefore clear them from the distribution

for root, dirs, files in os.walk(f"build/blessgen-{ver}"):
    for file in files:
        if file.startswith("api-ms") or file in ["ucrtbase.dll", "vcruntime140.dll"]:
            print(f"Strip file {file} from output...")
            os.unlink(os.path.join(root, file))
        elif "api-ms" in file:
            print(f"Not stripping {file}, but maybe should be?")

shutil.copy("LICENSE", f"build/blessgen-{ver}/LICENSE")
shutil.copy("readme.md", f"build/blessgen-{ver}/readme.md")
shutil.copy("changelog.txt", f"build/blessgen-{ver}/changelog.txt")
shutil.copy("effectenum.txt", f"build/blessgen-{ver}/effectenum.txt")

shutil.copytree("data", f"build/blessgen-{ver}/data")
os.mkdir(f"build/blessgen-{ver}/output")

# change working dir so the /build folder doesn't end up in the zip
os.chdir("build")

zipf = zipfile.ZipFile(f"blessgen-{ver}.zip", "w", zipfile.ZIP_DEFLATED)
for root, dirs, files in os.walk(f"blessgen-{ver}"):
    for file in files:
        zipf.write(os.path.join(root, file))

zipf.close()