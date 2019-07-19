# Requirements
- Path of Exile in 1920x1080 borderless fullscreen
- [Python 2.7.16](https://www.python.org/downloads/release/python-2716/)
- [Tesseract 5.0.0](https://github.com/UB-Mannheim/tesseract/wiki)
- [Java Version 8 Update 221](https://java.com/en/download/manual.jsp) (64-bit)
- [SikuliX 1.1.4](https://raiman.github.io/SikuliX1/downloads.html)
    - Jython interpreter 2.7.1
    - sikulix.jar

# Installation
1) Put the downloaded script contents, `jython-standalone-2.7.1.jar` and `sikulix.jar` into a new folder ([Like this](https://i.imgur.com/TGdpbdD.png))
2) Copy the file `poe` from `resource/tesseract` into your Tesseract configs folder, which is most likely located at `C:/Program Files/Tesseract-OCR/tessdata/configs`
3) Run `install.cmd`

# Usage
### Capture jewels
Start the capture script by running `run_capture.cmd`. It will take some seconds to start up and your mouse might jerk for a split-second, don't worry if that happens.

To capture jewels, position the jewel in the middle of the screen slightly to the left, but make sure all nodes in the jewel radius are visible. [Here's a screenshot](https://i.imgur.com/QWpc3K5.jpg) of what it should ideally look like. If you have any jewels socketed in this socket, remove them.

Press `F2` and wait until something happens or a message box shows up. If you set everything up correctly, the script will start capturing the normal nodes around the jewel socket. After that, a message will pop up telling you exactly what to do.

You can press `F4` to stop the script.

### Analyze jewels
After you captured some jewels, they need to be analyzed, because right after capturing them they're basically only screenshots of the passive skill tree. To do that, run `run_analyzer.cmd`. You don't need to do anything during this part, this script will automatically analyze everything. Once it's finished, you can find the analyzed jewels in the `result/` folder.

### Viewing jewels
You can open `viewer.html` in your browser, select the `.json` files from the `result/` folder and display the jewels in a readable format.

<img width="‭384‬" height="216" src="https://i.imgur.com/j5KhuyF.png">

### Tips
- When capturing jewels
	- Go into a town instead of your hideout
	- Disable Life/ES/Mana values above the globes in the UI options
	- Close your inventory

# Troubleshoot
You may need to add Python, pip and tesseract to your PATH environment variable:
- Open `Edit the system environment variables`
- Click `Environment Variables...` in the window that pops up
- Choose `Path`, click `Edit...`
- Click `New`, enter `C:\Python27`
- Repeat the same for `C:\Python27\Scripts` and `C:\Program Files\Tesseract-OCR`

*(You need to adjust these paths if you installed Python/Tesseract somewhere else)*

### `install.cmd` or `run_analyzer.cmd` still don't work after that
- `pip` with `C:\Python27\Scripts\pip`
- `python` with `C:\Python27\python`

### `run_capture.cmd` does not work
Try downloading `sikulixapi.jar`, place it into the folder and run `run_capture_api.cmd` instead. You may need to redownload the Jython interpreter 2.7.1 again.

### The analyzer isn't doing anything
- The analyzer will only do something if you captured jewels before. If the `data/jewel` and `data/timeless` folders are empty, it won't do anything.
- Make sure you're using Python 2, Python 3 may not be compatible with this script.
