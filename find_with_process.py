import tempfile
from multiprocessing import RLock as PRLock, Queue, Pool, cpu_count
import timeit
import logging
import shutil
import uuid
from pathlib import Path
from tabulate import tabulate

from bm import boyer_moore_search as bm_search

chunk_data = Queue()
file_write_lock = PRLock()
format = "%(processName)s %(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

def get_files(path: Path):
    files = []
    for file in path.iterdir():
        if file.is_file():
            files.append(file)
    return files


def create_temporary_files(file_path, tmp_path, text):
    file_index = 0
    encoded_text = text.encode("utf-8")
    with tempfile.NamedTemporaryFile(
            delete=False,
            dir=Path(tmp_path),
            prefix=str(uuid.uuid4()),
            suffix=".tmp",
    ) as tmpfile:
        tmpfile.write(encoded_text)  # Write the encoded text to the temporary file
        file_index += 1
        chunk_data.put({file_path: tmpfile.name})
    return 1


def read_in_chunks(file_object, word_amount=1000):
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


def process_data(files, tmp_dir):
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            for piece in read_in_chunks(f):
                create_temporary_files(file, tmp_dir, piece)


def search_in_file(args):
    pattern, file_path, tmp_file = args
    result = []
    with open(tmp_file, "r", encoding="utf-8-sig") as text:
        text_to_search = text.read()
        position = bm_search(text_to_search, pattern)
        if position != -1:
            result.append((file_path, position))
    return result

def find_pattern(pattern, chunk_data):
    result = []
    if chunk_data.empty():
        print("No files found")
        return result

    args_list = []
    while not chunk_data.empty():
        tmp_dict = chunk_data.get()
        file_path, tmp_file = next(iter(tmp_dict.items()))
        args_list.append((pattern, file_path, tmp_file))

    with Pool(cpu_count()) as pool:
        results = pool.map(search_in_file, args_list)
        for res in results:
            result.extend(res)
        pool.close()
        pool.join()

    return result

def save_results_to_txt(results, file_path):
    result_dict = {}
    for result in results:
        if result[0] not in result_dict:
            result_dict[result[0]] = 1
        else:
            result_dict[result[0]] += 1

    with file_write_lock:
        with open(file_path, "a") as file:
            table_data = [(orig_file, count) for orig_file, count in result_dict.items()]
            table = tabulate(table_data, headers=["File Path", "Count"], tablefmt="grid")
            file.write(table)


def main():
    tmp_dir = Path(r".\tmp")
    files = get_files(Path(r".\texts"))
    pattern = "something"
    file_name = "readme.md"
    with open(file_name, "w") as file:
        file.write(f"Results for pattern '{pattern}':\n")
    if not Path.exists(tmp_dir):
        try:
            Path.mkdir(tmp_dir)
        except OSError:
            print(f"Creation of the directory {tmp_dir} failed")

    process_data(files, tmp_dir)
    save_results_to_txt(find_pattern(pattern, chunk_data), file_name)

    if Path.exists(tmp_dir):
        try:
            shutil.rmtree(tmp_dir)
        except OSError:
            print(f"Deletion of the directory {tmp_dir} failed")


if __name__ == "__main__":
    time = timeit.timeit("main()", number=5)
    main()
    with open("readme.md", "a") as file:
        file.write(f"\nTime with process: {round(time, 3)} s")
