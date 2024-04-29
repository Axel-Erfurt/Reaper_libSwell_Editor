# Reaper_libSwell_Editor
edit libSwell.colortheme on Linux

Note: leave font face and font size in the first and second row

## Requirements
- python3
- python3-gi

## Usage

```python3 /path/to/libswell_editor.py```

opens the *libSwell.colortheme* from the default path */home/username/.config/REAPER*

```python3 /path/to/libswell_editor.py /path/to/libSwell.colortheme```

opens  the file with the specified path

*backup file with timestamp will be created on opening the file*

- color preview on selecting a row that contains a color
- change the font with the FontSelector button
- change integer values with the SpinBox buttons
- change colors by double-clicking the row, this opens a color selection window
- activate / deactivate line with the button on top

![screenshot](https://github.com/Axel-Erfurt/Reaper_libSwell_Editor/blob/main/screenshot.png?raw=true)
