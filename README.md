# Messaging Application

## Description
This is a two-person, locally hosted, secure messaging application.

## Use

### Setup
1. Install python at: https://www.python.org/downloads/
2. Check if installed correctly:
   ```bash
   python --version
   ``` 
4. Create a local version of this repository.
5. Install all necessary dependencies:
   ```bash
   pip install pycryptodome
   ```
3. Make sure the repository has access to all Python modules.

### Run
1. Navigate to the repository in the command line
2. Use the following command to run the project:
```bash
python boot.py
```
3. The server should start up and two chat windows should pop up

## Features
- Input username in both client windows.
- Click **Join**.
- Input key in both client windows.
- Choose encryption bit value.

### To Send Messages
- Type in the bottom textbox.
- Click **Text** to send the message to the other user.

### To Send Files
- Place the desired file in the root repository folder.
- Type the name of the file in the bottom textbox (including the extension).
- Click **File** to send the file to the other user.

### Notes
- For the receiver to see the messages and files, the inputted key and bit must match that of the sender.

