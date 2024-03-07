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


chunk_data = TempFileHashTable()

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


def create_temporary_files(file_path, text, tmpfile_names: list):
    file_index = 0
    encoded_text = text.encode("utf-8")
    with tempfile.NamedTemporaryFile(
        delete=False,
        prefix=f"chunk{file_index}_",
        suffix=".tmp",
    ) as tmpfile:
        tmpfile.write(encoded_text)  # Write the encoded text to the temporary file
        file_index += 1
        tmpfile_names.append(tmpfile.name)
    chunk_data.add_temp_file(file_path, tmpfile_names)
    return 1


def read_in_chunks(file_object, word_amount=1000):
    """Lazy function (generator) to read a file piece by piece without splitting words."""
    while True:
        data = ""
        word_count = 0
        while word_count < word_amount:
            char = file_object.read(1)
            if not char:
                break
            data += char
            if char.isspace():
                word_count += 1
        if not data:
            break
        yield data


def process_data(files):
    tmpfile_names = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            for piece in read_in_chunks(f):
                create_temporary_files(file, piece, tmpfile_names)


def find_pattern(pattern):
    result = []
    if not chunk_data.hash_table:
        return
    for path, tmp_files in chunk_data.hash_table.items():
        for tmp_file in tmp_files:
            with open(tmp_file, "r", encoding="utf-8-sig") as text:
                text_to_search = text.read()
                position = bm_search(text_to_search, pattern)
                if position != -1:
                    result.append(path)
    return result


def main():
    files = get_files(Path(r".\texts"))
    process_data(files)
    print(find_pattern(r"i am so lonely"))


if __name__ == "__main__":
    main()