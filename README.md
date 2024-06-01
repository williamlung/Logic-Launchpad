
# Logic Launchpad
Logic LaunchPad is an intuitive platform designed specifically for teaching the C programming language. It enables educators to effortlessly create and manage question sets and test cases tailored to C programming. Students can engage with and solve these problems in a seamless environment, enhancing their understanding of C syntax, concepts, and problem-solving skills.

![llp2](https://github.com/williamlung/Logic-Launchpad/assets/112676745/76f0c844-8eee-4295-9495-c973bbc7b7f3)

![llp](https://github.com/williamlung/Logic-Launchpad/assets/112676745/822c61d8-2f3a-4e8a-85b4-f6429741b552)

Main Techniques:  
Programming Languages: Python  
Frontend: Pyside6  
Backend: Django, Docker  

## Installing the environment
Prepare the Python environment for running the backend server and frontend program  
Python version: 3.10  
```
pip install -r requirements.txt
```


## Getting Started
> [!WARNING]
> This is not for production, Please check [the Django Official Documentation](https://docs.djangoproject.com/en/5.0/howto/deployment/).

> [!IMPORTANT]
> Before you start the Django server, make sure your **Docker** is able to run.  
> because all test cases are using the gcc Docker to compile and run the code  
First, start the Django backend  
```
cd backend
python manage.py runserver 0.0.0.0:38000 --insecure
```
Run the manager_main.py for managing the questions set, test cases, and users.
```
cd frontend
python manager_main.py
```
After adding questions, if you want the student to work on week 1's questions, update the variable WEEK to 1 in backend/api_server/settings.py.  
You can then see week 1's questions by running client_main.py  
```
cd frontend
python client_main.py
```
## Building the app
You can use either Windows or Mac OS to build the corresponding executable file.  
It may trigger a false alarm from the OS firewall.  
Please check how to add an exception for the program in [Windows](https://support.microsoft.com/en-us/windows/add-an-exclusion-to-windows-security-811816c0-4dfd-af4a-47e4-c301afe13b26) or [Mac](https://support.apple.com/en-us/102445)  
```
cd frontend
pyinstaller client_main.py --onefile --windowed --add-data asserts\icon\ios\AppIcon~ipad.png:icon\ios\ --icon=\asserts\icon\web\icon-512.png
pyinstaller manager_main.py --onefile --windowed --add-data asserts\icon\ios\AppIcon~ipad.png:icon\ios\ --icon=\asserts\icon\web\icon-512.png
```
