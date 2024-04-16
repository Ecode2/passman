from cx_Freeze import setup, Executable, finder


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
        copyright="E_code ltd"
        )]
)