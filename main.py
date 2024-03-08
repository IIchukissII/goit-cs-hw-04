import tempfile
import threading
import timeit
from pathlib import Path
from queue import Queue
from tabulate import tabulate

from bm import boyer_moore_search as bm_search

chunk_data = Queue()


def get_files(path: Path):
    files = []
    for file in path.iterdir():
        if file.is_file():
            files.append(file)
    return files


def create_temporary_files(file_path, text):
    file_index = 0
    encoded_text = text.encode("utf-8")
    with tempfile.NamedTemporaryFile(
            delete=False,
            prefix=f"chunk{file_index}_",
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


def process_data(files):
    tmpfile_names = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            for piece in read_in_chunks(f):
                create_temporary_files(file, piece)


def find_pattern(pattern):
    result = []
    if chunk_data.empty():
        print("No files found")
        return

    def search_in_file(pattern, result, file_path, tmp_file):
        with open(tmp_file, "r", encoding="utf-8-sig") as text:
            text_to_search = text.read()
            position = bm_search(text_to_search, pattern)
            if position != -1:
                result.append((file_path, position))

    threads = []
    while not chunk_data.empty():
        # Get the dictionary from the queue
        tmp_dict = chunk_data.get()

        # Extract the key and value using a dictionary comprehension
        file_path, tmp_file = next(iter(tmp_dict.items()))
        thread = threading.Thread(target=search_in_file, args=(pattern, result, file_path, tmp_file))
        threads.append(thread)
        thread.start()

            # Check the number of active threads
        #active_threads = sum(1 for thread in threads if thread.is_alive())
        #print(f"Number of active threads: {active_threads}")

    for thread in threads:
        thread.join()
    return result


# Create a threading lock
file_write_lock = threading.RLock()


def save_results_to_txt(results, file_path, pattern=""):
    result_dict = {}
    for result in results:
        if result[0] not in result_dict:
            result_dict[result[0]] = 1
        else:
            result_dict[result[0]] += 1

    with file_write_lock:
        with open(file_path, "w") as file:
            file.write(f"Results for pattern '{pattern}':\n\n")
            table_data = [(orig_file, count) for orig_file, count in result_dict.items()]
            table = tabulate(table_data, headers=["File Path", "Count"], tablefmt="grid")
            file.write(table)


def main():
    files = get_files(Path(r".\texts"))
    pattern = "God"
    process_data(files)
    save_results_to_txt(find_pattern(pattern), "results.txt", pattern)


if __name__ == "__main__":
    main()
    timeit.timeit("main()", number=1)
