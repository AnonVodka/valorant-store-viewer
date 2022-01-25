pyinstaller --noconfirm --onedir --console --icon "./assets/icon.ico" --name "vsv" "./main.py" --distpath "./compiled"
pyinstaller --noconfirm --onedir --console --icon "./assets/icon.ico" --name "vsv-discord" "./main_discord.py" --distpath "./compiled" 
pyinstaller --noconfirm --onedir --console --icon "./assets/icon.ico" --name "vsv-single" "./main_single.py" --distpath "./compiled"