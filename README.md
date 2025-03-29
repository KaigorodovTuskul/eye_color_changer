# Video eye color changer
Video eye color changer using opencv and mediapipe.  
### Before and After
<img src="images/before.PNG" width="45%"> <img src="images/after.PNG" width="45%">
### :pencil2: Quick start
1. Download the repo or git clone repo. Create "workfolder" folder if you dont have one and put your video.
2. Install dependencies:
```sh
pip install -r requirements.txt
```
or 
Run install_portable.bat
```bash
install_portable.bat
```
3. If you dont have installed version of ffmpeg, or you want to use different version (or not locally) then you need to download and install ffmpeg from here https://ffmpeg.org/download.html (this build was tested on ffmpeg-7.0.2-full_build)
Edit stable_CPU_silent.py and find these variables:
```py
ffmpeg_path = r'your path to your ffmpeg.exe'
ffprobe_path = r'your path to your ffprobe.exe'
```
Write your paths here, or if you already have installed version of ffmpeg and have these variables on environment variables then you can just type ffmpeg and ffprobe.
4. Run start_portable.bat to activate virtual environment and start the proccess.
```bash
start_portable.bat
```
### :computer: Command Line
```bash
$ python stable_CPU_silent.py --input-source [SOURCE] --output-name [OUTPUT] --clean-cache [MODE] --silent-mode [MODE] --sbs-mode [MODE] --strength [STRENGTH] --rgb [RGB]
```
* `--input-source [SOURCE]` (optional): Specify your path to video in this argument if you want to use unique arguments. Default: code will process all files in "workfolder" folder.
* `--output-name [OUTPUT]` (optional): Specify name to output video in this argument if you want to use unique arguments. Default: every video in "workfolder" folder will take "output" and "rgb" suffix.
* `--clean-cache [MODE]` (optional): If use then code will clear temp folders. Default: off
* `--silent-mode [MODE]` (optional): If you want to run the code in silent mode it will not showing the real-time cv processing window. Default: off 
* `--sbs-mode [MODE]` (optional): If you want to process a video that have sbs format it will crop video side by side and then merge them. Default: off
* `--strength [STRENGTH]`: Default: 0.4
* `--rgb [RGB]`: You can choose output eye color by typing RGB in format '30, 0, 0' or just type the color. List of supporting colors: ['black', 'white', 'blue', 'red', 'green', 'yellow', 'brown']
    


