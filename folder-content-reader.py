import os
from typing import Iterator, Tuple

def get_tree_structure(start_path: str) -> str:
    """
    Generate a string representation of the directory tree structure.

    Args:
        start_path (str): The root directory to start the tree structure from.

    Returns:
        str: A string representation of the directory tree structure.
    """
    def walk_directory(dir_path: str, prefix: str = "") -> Iterator[Tuple[str, str, bool]]:
        """
        Generator function to walk through the directory structure.

        Args:
            dir_path (str): The current directory path.
            prefix (str): The prefix to use for the current level in the tree.

        Yields:
            Tuple[str, str, bool]: A tuple containing the current prefix, 
                                   the os.DirEntry object, and a boolean 
                                   indicating if it's the last entry.
        """
        # Get and sort directory entries, excluding hidden folders
        entries = sorted(os.scandir(dir_path), key=lambda e: e.name.lower())
        entries = [e for e in entries if e.name not in {'.git', '.idea', '__pycache__'}]
        
        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            yield prefix, entry, is_last

            if entry.is_dir():
                # Recursively walk through subdirectories
                extension = '    ' if is_last else '│   '
                yield from walk_directory(entry.path, prefix + extension)

    lines = []
    for prefix, entry, is_last in walk_directory(start_path):
        # Choose the appropriate connector symbol
        connector = '└── ' if is_last else '├── '
        # Add directory indicator '/' for directories
        lines.append(f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")

    return '\n'.join(lines)

def get_file_contents(file_path: str) -> str:
    """
    Read and return the contents of a file.

    Args:
        file_path (str): The path to the file to be read.

    Returns:
        str: The contents of the file, or an error message if the file cannot be read.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def main() -> None:
    """
    Main function to generate the folder contents file.
    """
    # Get the directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = 'folder_contents.txt'
    script_name = os.path.basename(__file__)

    # Get the name of the current folder
    folder_name = os.path.basename(current_dir)

    with open(output_file, 'w', encoding='utf-8') as out_file:
        # Write the folder name and tree structure
        out_file.write(f"{folder_name}/\n")
        out_file.write(get_tree_structure(current_dir))
        out_file.write("\n\n")

        # Write the contents of each file
        for root, _, files in os.walk(current_dir):
            for file in files:
                # Skip the output file and the script itself
                if file not in {output_file, script_name}:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, current_dir)
                    out_file.write(f"### `{relative_path}` file:\n\n```\n")
                    out_file.write(get_file_contents(file_path))
                    out_file.write("\n```\n\n")

    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()
    
# python folder-content-reader.py
