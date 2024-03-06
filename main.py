import tempfile
from pathlib import Path
from bm import boyer_moore_search


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


def create_temporary_files(files, chunk_size):
    chunk_data = TempFileHashTable()
    tmpfile_names = []
    for file in files:
        with open(file, "rb") as infile:
            file_index = 0
            while True:
                chunk = infile.read(chunk_size)
                if not chunk:
                    break
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    prefix=f"{file.name}_chunk{file_index}_",
                    suffix=".tmp",
                ) as tmpfile:
                    tmpfile.write(chunk)
                    file_index += 1
                    tmpfile_names.append(tmpfile.name)
        chunk_data.add_temp_file(file, tmpfile_names)
    return chunk_data.hash_table


def main():
    files = get_files(Path(r".\texts"))
    tmp_files = create_temporary_files(files, chunk_size=1024)

    for input_file, temp_files in tmp_files.items():
        for temp_file in temp_files:
            with open(temp_file, "rb") as f:
                print(f.read())


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
