print("You should be using .venv virtual environment. To activate,"
      "simply open a .py file like this and open a new terminal. It'll do the"
      "rest if your VS Code has previously used a venv in this folder.")

print("\nIn terminal, to start an app, use 'cd <project folder>' and then \n'py manage.py"
      " runserver'")


choice = input("Do you need the LAN address for this machine? (Y/N):  ")
if (choice.upper() == "Y"):
    import socket
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    print(f'Your LAN address is: {IPAddr}')

# name = 'Andrew'
# print(name.upper())


# to install virtual environment, run this in terminal:
# py -m venv .venv

# to activate: 
# & path\to\.venv\Scripts\Activate.ps1

# Then, make sure VS Code's interpreter is the same as the .venv's interpreter


# if scripts are disabled for powershell, 
# https://tecadmin.net/powershell-running-scripts-is-disabled-system/

# https://youtu.be/ZsJRXS_vrw0