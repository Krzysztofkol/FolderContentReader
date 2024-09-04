import os
import re
from typing import Iterator, Tuple, List, Optional, Set
from collections import defaultdict
import concurrent.futures
import fnmatch

# New ignore lists for structure and content
STRUCTURE_IGNORED_PATHS = {
    '.git',
    'customised-folder-content-reader.py',
    'customised-folder-content-reader-launcher.bat'
}

CONTENT_IGNORED_PATHS = {
    'README.md',
    '.git'
}

CONTENT_IGNORED_EXTENSIONS = {
    'git',
    'gitignore',
    'bat',
    '',
}

def normalize_line_endings(content: str) -> str:
    """Normalize line endings to Unix-style (\n)."""
    return content.replace('\r\n', '\n').replace('\r', '\n')

def path_should_be_ignored(path: str, root: str, ignore_list: set) -> bool:
    rel_path = os.path.relpath(path, root).replace(os.sep, '/')  # Normalize path separators
    
    # Check if it's a hidden file or folder
    if os.path.basename(path).startswith('.'):
        return True

    for ignored_path in ignore_list:
        if ignored_path.startswith('**'):
            # Handle patterns like '**/*.bat'
            if fnmatch.fnmatch(rel_path, ignored_path) or fnmatch.fnmatch(os.path.basename(path), ignored_path[3:]):
                return True
        elif fnmatch.fnmatch(rel_path, ignored_path):
            return True
        # Check if any parent directory matches the ignore pattern
        parts = rel_path.split('/')
        for i in range(len(parts)):
            if fnmatch.fnmatch('/'.join(parts[:i+1]), ignored_path):
                return True
    return False

def get_dir_info(dir_path: str, root: str) -> Tuple[int, int]:
    total_size = 0
    item_count = 0
    for root_path, dirs, files in os.walk(dir_path, topdown=True):
        dirs[:] = [d for d in dirs if not path_should_be_ignored(os.path.join(root_path, d), root, STRUCTURE_IGNORED_PATHS)]
        files = [f for f in files if not path_should_be_ignored(os.path.join(root_path, f), root, STRUCTURE_IGNORED_PATHS)]
        item_count += len(files)
        for file in files:
            file_path = os.path.join(root_path, file)
            total_size += os.path.getsize(file_path)
    return total_size, item_count

def walk_directory(dir_path: str, root: str, script_name: str, output_file: str, excluded_formats: List[str]) -> Iterator[Tuple[str, os.DirEntry, bool, Optional[int], Optional[int]]]:
    entries = list(os.scandir(dir_path))
    entries = [e for e in entries if not path_should_be_ignored(e.path, root, STRUCTURE_IGNORED_PATHS) and e.name not in {script_name, output_file}]
    
    info_cache = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_entry = {executor.submit(get_dir_info, entry.path, root) if entry.is_dir() else executor.submit(lambda: (entry.stat().st_size, 1)): entry for entry in entries}
        for future in concurrent.futures.as_completed(future_to_entry):
            entry = future_to_entry[future]
            info_cache[entry] = future.result()
    
    sorted_entries = sorted(entries, key=lambda e: (-info_cache[e][1], -info_cache[e][0], e.name.lower()))
    
    for i, entry in enumerate(sorted_entries):
        is_last = (i == len(sorted_entries) - 1)
        size, count = info_cache[entry]
        yield dir_path, entry, is_last, size, count
        if entry.is_dir():
            yield from walk_directory(entry.path, root, script_name, output_file, excluded_formats)

def get_tree_structure(start_path: str, script_name: str, output_file: str, excluded_formats: List[str]) -> str:
    lines = []
    prefix_map = defaultdict(lambda: "")
    for dir_path, entry, is_last, size, count in walk_directory(start_path, start_path, script_name, output_file, excluded_formats):
        depth = len(os.path.relpath(dir_path, start_path).split(os.sep)) - 1
        prefix = prefix_map[dir_path]
        connector = '└── ' if is_last else '├── '
        name_with_indicator = f"{entry.name}{'/' if entry.is_dir() else ''}"
        lines.append(f"{prefix}{connector}{name_with_indicator}")
        if entry.is_dir():
            new_prefix = prefix + ('    ' if is_last else '│   ')
            prefix_map[entry.path] = new_prefix
    return '\n'.join(lines)

def get_file_contents(file_path: str) -> Optional[str]:
    try:
        with open(file_path, 'r', encoding='utf-8', newline=None) as file:
            content = file.read()
        return normalize_line_endings(content)
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None

def process_file(file_info: Tuple[str, int, str], current_dir: str, excluded_formats: List[str], ignored_extensions: Set[str]) -> Optional[str]:
    file_path, _, file_contents = file_info
    relative_path = os.path.relpath(file_path, current_dir)
    
    # Check if the file should be ignored based on CONTENT_IGNORED_PATHS
    if path_should_be_ignored(file_path, current_dir, CONTENT_IGNORED_PATHS):
        return None
    
    file_extension = os.path.splitext(file_path)[1][1:].lower()  # Get the file extension without the dot and convert to lowercase
    
    # Check if the file extension is in CONTENT_IGNORED_EXTENSIONS
    if file_extension in ignored_extensions:
        return None
    
    if file_extension not in excluded_formats:
        normalized_contents = normalize_line_endings(file_contents)
        return f"### `{relative_path}`:\n```{file_extension}\n{normalized_contents}\n```"
    return None

def process_output_file(file_path: str) -> None:
    with open(file_path, 'r', encoding='utf-8', newline=None) as file:
        content = file.read()
    content = normalize_line_endings(content)
    content = re.sub(r'\n+', '\n', content)
    content = re.sub(r'\s+\n', '\n', content)
    content = content.rstrip('\n')  # Remove trailing newlines
    with open(file_path, 'w', encoding='utf-8', newline='\n') as file:
        file.write(content)

def main() -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__)
    folder_name = os.path.basename(current_dir)
    output_file = f"{folder_name}_codebase.md"
    
    excluded_formats = [""]  # exclude the listed formats; "" means excluding files without format

    file_info: List[Tuple[str, int, Optional[str]]] = []
    
    with open(output_file, 'w', encoding='utf-8', newline='\n') as out_file:
        out_file.write("# Codebase:\n")
        out_file.write("## Folder Contents:\n")
        out_file.write("### Folder structure:\n")
        out_file.write(f"```\n{folder_name}/\n")
        tree_structure = get_tree_structure(current_dir, script_name, output_file, excluded_formats)
        out_file.write(tree_structure)
        out_file.write("\n```\n")
        out_file.write("## File Contents:\n")
        
        for dir_path, entry, _, size, _ in walk_directory(current_dir, current_dir, script_name, output_file, excluded_formats):
            if entry.is_file():
                file_path = os.path.join(dir_path, entry.name)
                file_info.append((file_path, size))
        
        file_info.sort(key=lambda x: x[1], reverse=True)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(get_file_contents, fi[0]): fi for fi in file_info}
            results = []
            for future in concurrent.futures.as_completed(future_to_file):
                file_path, size = future_to_file[future]
                file_contents = future.result()
                if file_contents is not None:
                    results.append((file_path, size, file_contents))
        
        results.sort(key=lambda x: x[1], reverse=True)
        for file_path, size, file_contents in results:
            processed_file = process_file((file_path, size, file_contents), current_dir, excluded_formats, CONTENT_IGNORED_EXTENSIONS)
            if processed_file:
                out_file.write(processed_file + "\n")
    
    process_output_file(output_file)
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()