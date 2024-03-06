import argparse
import logging
from pathlib import Path
from shutil import copyfile
from threading import Thread
import tempfile

parser = argparse.ArgumentParser(description="Find pattern in text files")
parser.add_argument("--source", "-s", required=True, help="Source dir")
args = vars(parser.parse_args())

source = Path(args["source"])

files = []

chunk_size = 1024  # specify the chunk size
with open('input.txt', 'r') as infile:
    with tempfile.TemporaryFile() as tmpfile:
        chunk = infile.read(chunk_size)
        while chunk:
            tmpfile.write(chunk)
            chunk = infile.read(chunk_size)
        # Do other work with the temporary file here


def get_files(path: Path):
    for file in path:


def get_folders(path: Path):
    for file in path.iterdir():
        if file.is_dir():
            folders.append(file)
            get_folders(file)


def copy_files(path: Path, dest: Path):
    for file in path.iterdir():
        if file.is_file():
            folder = dest / file.suffix[1:]
            try:
                folder.mkdir(exist_ok=True, parents=True)
                copyfile(file, folder / file.name)
            except OSError as e:
                logging.error(e)


if __name__ == "__main__":
    format = "%(threadName)s %(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    folders.append(source)
    get_folders(source)
    print(folders)

    threads = []
    for folder in folders:
        thread = Thread(target=copy_files, args=(folder, output))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"All files copied to {output}. Source dir will be deleted")
