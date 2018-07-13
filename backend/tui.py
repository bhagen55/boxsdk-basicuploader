import boxinterface
from blessings import Terminal
from pathlib import Path
import sys, signal

t = Terminal()

current_folder = None
folder_queue = []
box_interface
box = None

# to handle sigint

def signal_handler(sig, frame):
    print("\nExiting")
    sys.exit()
signal.signal(signal.SIGINT, signal_handler)


# Checks that the proper folder structure exists
#   ./keys and ./upload should exist
#   does not check for existence of the appauth.json but asks that it be put
#   in ./keys if the folder doesn't exist.
#
# Authenticates then launches the main menu
def initmenu():
    global client, current_folder, box
    print(t.clear)
    print(t.bold + t.underline + ('Box TUI\n\n') + t.normal)

    # print("Checking if folder structure exists...")
    # if not Path("./keys").is_dir():
    #     print("keys directory not created!")
    #     print("Creating keys directory...")
    #     box.create_folder_structure()
    #     print("Please place box api json authentication file in the keys directory\n"
    #             "and name it appauth.json then re-run script")
    #     sys.exit()
    # elif not Path("./upload").is_dir():
    #     print("Creating upload folder...")
    #     box.create_folder_structure()

    print(t.clear)
    print("Authenticating...")
    box = box_interface.box_interface("./keys/appauth.json")

    current_folder = box.get_folder('0')
    print(current_folder)
    folder_queue.append(current_folder)
    mainmenu()


# Lists items in the current folder and actions to take on them
def mainmenu():
    global current_folder, folder_queue, box
    while True:
        print(t.clear)

        current_location = ""
        for folder in folder_queue:
            current_location = current_location + folder['name'] + '/'
        print(t.underline + "Current Location: " + current_location + t.normal)

        items = box.get_folder_contents(current_folder)
        i = 1
        for item in items:
            if item['type'] == "folder":
                print(t.underline + str(i) + ": " + item['name'] + t.normal)
            if item['type'] == "file":
                print(str(i) + ": " + item['name'])
            i = i+1

        print()
        choice = input(
                        "Choose a file by number or enter command:\n"
                        + t.green + "b to go back.\n"
                        "n to make a new folder.\n"
                        "u to upload to this folder.\n"\
                        "r to rename this folder.\n"
                        "d to delete this folder.\n"
                        + t.normal + ": " )

        if choice == 'b':
            if len(folder_queue) != 1:
                folder_queue.pop()
                current_folder = folder_queue[len(folder_queue) -1]
        elif choice == 'n':
            createfoldermenu(current_folder)
        elif choice == 'u':
            uploadmenu(current_folder)
        elif choice == 'r':
            renamemenu(current_folder)
        elif choice == 'd':
            deletemenu(current_folder)
        elif items[int(choice) - 1]['type'] == "folder":
            current_folder = items[int(choice) - 1]
            folder_queue.append(current_folder)
        elif items[int(choice) - 1]['type'] == "file":
            filemenu(items[int(choice) - 1])


def filemenu(file):
    print(t.clear)
    print(t.underline + "File Menu:" + t.normal)
    print(t.bold + "Selected: " + file['name'] + t.normal)
    choice = input(
        t.green + "l. Get direct download link\n"
        "d. Delete file\n"
        "r. Rename file\n"
        + t.normal + ": "
    )

    if choice is 'l':
        with t.location(0, t.height-1):
            print(box.get_direct_download(file))
    elif choice is 'd':
        deletemenu(file)
    elif choice is 'r':
        renamemenu(file)


def renamemenu(item):
    if(item['id'] == '0'):
        print("Can't rename root folder!")
    else:
        print("Current name: " + item['name'])
        new_name = input("Input new name: ")

        if (item['type'] == "folder"):
            box.rename_folder(item, new_name)
            changed_name = box.get_folder(item['id'])['name']
        elif (item['type'] == "file"):
            box.rename_file(item, new_name)
            changed_name = box.get_file(item['id'])['name']

        print("Name is now " + changed_name)


def deletemenu(item):
    global folder_queue, current_folder
    if (item['id'] == '0'):
        print("Can't delete root folder!")
        result = False
    elif (item['type'] == "folder"):
        print("Delete even if the folder is not empty?")
        choice = input("y or n: ")
        if choice == "y":
            result = box.delete_folder(item, True)
        elif choice == "n":
            result = box.delete_folder(item, False)

        if result == True:
            folder_queue.pop()
            current_folder = folder_queue[len(folder_queue) -1]
    elif (item['type'] == "file"):
        box.delete_file(item)


def createfoldermenu(item):
    name = input("Name of new folder: ")
    box.create_folder(item, name)


def uploadmenu(item):
    print(t.clear)
    print("Uploading to folder " + item['name'])

    upload_folder_path = input("Enter path to upload folder")

    print("Contents of upload folder:\n")
    p = Path(upload_folder_path)
    for f in p.iterdir():
        print(f.name)
    print()

    file = Path(upload_folder_path + '/' + input("Enter file name in upload folder: "))

    box.upload(item, file)


if __name__ == '__main__':
    initmenu()
