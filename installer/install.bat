@echo off
mkdir studio-custom-names-installer-temp
cd studio-custom-names-installer-temp
echo Downloading Python...
powershell "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.2/python-3.12.2-embed-win32.zip -OutFile python-embed.zip"
echo Downloading pip...
powershell "Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py"
echo Downloading install script...
powershell "Invoke-WebRequest -Uri https://raw.githubusercontent.com/GSG-Robots/studio-custom-names/main/installer/install.py -OutFile install.py"
echo Extracting Python...
powershell "Expand-Archive .\python-embed.zip -DestinationPath .\python-embed"
echo Adding pip support...
powershell "Add-Content -Path .\python-embed\python312._pth -Value 'import site'"
echo Installing pip...
.\python-embed\python.exe .\get-pip.py
echo Installing requirements.txt...
.\python-embed\Scripts\pip.exe install requests
echo Running install script...
.\python-embed\python.exe .\install.py
pause