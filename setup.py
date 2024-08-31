from cx_Freeze import setup, Executable, finder
import sys

base=None
if sys.platform == "win32":
    base="Win32GUI"

def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()

setup(
    name= "Passman",
    version="1.0.2",
    author= "Abubakar Alaya",
    author_email = "ecode5814@gmail.com",
    license="MIT",
    include_package_data=True,
    description="A Password manager to secure and encrypt your sensitive information and files",
    executables=[Executable(
        script="passman.py",
        icon="assets/padlock.png",
        copyright="E_code ltd",
        base=base)],
    options={"build_exe":{"packages":read_requirements(),
            "include_files":["assets/", "database/database_table.json"]}}
)
