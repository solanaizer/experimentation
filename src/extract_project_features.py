import subprocess as sp
import os


def adjust_path_for_os(input_path):
    if os.name == 'nt':  # Windows
        # Replace Unix-style path separator '/' with Windows-style '\'
        return input_path.replace('/', r"\\")
    else:  # Unix/Linux
        # Ensure the path uses Unix-style separators '/'
        return input_path.replace(r"\\", '/')


def get_rust_paths(project_root_path):
    command = ' && '.join(["cd", f"cd {adjust_path_for_os(project_root_path)}", "find . -type f -name \"*.rs\""])

    process = sp.run(command, shell=True, check=True, stdout=sp.PIPE, stderr=sp.PIPE)

    # Getting the output and error (if any)
    output = process.stdout.decode()
    error = process.stderr.decode()

    if process.returncode == 0:
        print("Command executed successfully:")
        print(output)
    else:
        print("Error executing command:")
        print(error)


def main():
    project_directory = r"C:\Users\alexw\code\liquid-staking-program"

    get_rust_paths(project_directory)


if __name__ == "__main__":
    main()