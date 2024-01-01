import os 
import json
import shutil
from subprocess import PIPE, run
import sys


GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSTION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]

# Function to find paths of games
def find_all_game_paths(source):
    # List to hold game paths
    game_paths = []

    # Walk through files in directory of inputted source looking for the "game" pattern and adding that path to list
    for root, dirs, files in os.walk(source):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)
        # Break to only run once
        break

    return game_paths

# Function to create a file with desired meta data
def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }
    with open (path, "w") as f:
        json.dump(data, f)

# Function the copys the content of a file and writes it to the new file
def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source,dest)

# Function to compile the game code in the project folder
def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files: 
            if file.endswith(GAME_CODE_EXTENSTION) :
                code_file_name = file
                break
        break    

    if code_file_name is None:
        return

    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)

# Function to run 
def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)

    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("compile result", result)

    os.chdir(cwd)

def main(source, target):
    # Get CWD
    cwd = os.getcwd()
    # Assign source path to variable
    source_path = os.path.join(cwd, source)
    # Assign Target path
    target_path = os.path.join(cwd, target)

    # Gather list of paths
    game_paths = find_all_game_paths(source_path)
   
    # Create new directories with cleaner titles
    new_game_dirs = get_name_from_paths(game_paths, "_game")
    
    # Create directory to contain new game directories
    create_dir(target_path)
    
    
    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)

    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)



    
# Function to remove the "_game" from the name to clean the data
def get_name_from_paths(paths, to_strip):
    
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)
    return new_names

def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        raise Exception("You must pass source and target directory only.")
    
    source, target = args[1:]
    main(source, target)

