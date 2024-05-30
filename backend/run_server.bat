
@echo off

REM Check for all user installation
if exist "%ProgramData%\Anaconda3" (
    set "anaconda_path=%ProgramData%\Anaconda3"
) else (
    REM Check for single user installation
    if exist "%USERPROFILE%\Anaconda3" (
        set "anaconda_path=%USERPROFILE%\Anaconda3"
    ) else (
        echo Anaconda installation not found.
        exit /b 1
    )
)

call "%anaconda_path%\Scripts\activate.bat" c_practice_backend
python manage.py runserver 0.0.0.0:38000
pause