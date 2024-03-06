import tempfile
from pathlib import Path
from bm import boyer_moore_search as bm_search


class TempFileHashTable:
    def __init__(self):
        self.hash_table = {}

    def add_temp_file(self, key, file_path):
        self.hash_table[key] = file_path

    def get_temp_file(self, key):
        return self.hash_table.get(key)

    def remove_temp_file(self, key):
        if key in self.hash_table:
            del self.hash_table[key]


def get_files(path: Path):
    """
    Function to get a list of files in the specified path.

    Args:
        path (Path): The path to the directory from which files will be retrieved.

    Returns:
        list: A list of files in the specified path.
    """
    files = []
    for file in path.iterdir():
        if file.is_file():
            files.append(file)
    return files


data = TempFileHashTable()


import tempfile

def read_text_in_chunks(file_paths, chunk_size, encoding='utf-8-sig'):
    for file_path in file_paths:
        with open(file_path, 'r', encoding=encoding) as file:
            word_buffer = ""
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    if word_buffer:
                        yield word_buffer
                    break
                words = chunk.split()
                if len(word_buffer) + len(words[0]) > chunk_size:
                    yield word_buffer
                    word_buffer = ""
                for word in words:
                    if len(word_buffer) + len(word) <= chunk_size:
                        word_buffer += " " + word if word_buffer else word
                    else:
                        yield word_buffer
                        word_buffer = word

def save_chunks_to_temp_file(chunks):
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    for chunk in chunks:
        temp_file.write(chunk + "\n")
    temp_file_path = temp_file.name
    temp_file.close()
    return temp_file_path

def save_paths_to_hash_table(file_paths, temp_file_paths):
    hash_table = {}
    for i in range(len(file_paths)):
        hash_table[file_paths[i]] = temp_file_paths[i]
    return hash_table

def get_temp_file_path(hash_table, query_file_path):
    return hash_table.get(query_file_path, "File path not found in hash table")


def find_pattern_in_text(pattern, chunk_data):
    for temp_file in chunk_data:
        with open(temp_file, "r", encoding="utf-8") as f:
            try:
                chunk_text = f.read()
            except UnicodeDecodeError:
                continue
            if bm_search(chunk_text, pattern):
                print(f"Pattern found in {temp_file}")


def main():
    files = get_files(Path(r".\texts"))
    temp_files = create_temporary_files(files, chunk_size=100)
    pattern = "then"
    find_pattern_in_text(pattern, temp_files)


if __name__ == "__main__":
    main()