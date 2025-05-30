# with open("temp.txt", mode="a") as fp:
#     fp.write("\navah, dddasd, sfscs")
for i in range(7):
    print(f"F{i}")
    if i == 3:
        continue
    print(f"L{i}")

import os

class CrdownloadChecker:
    def __init__(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError(f"The path '{folder_path}' is not a valid directory.")
        self.folder_path = folder_path

    def count_crdownload_files(self):
        """Count the number of .crdownload files in the folder."""
        return sum(
            1 for file in os.listdir(self.folder_path)
            if file.endswith('.crdownload') and os.path.isfile(os.path.join(self.folder_path, file))
        )

    def get_crdownload_filenames(self):
        """Return a list of .crdownload file names in the folder."""
        return [
            file for file in os.listdir(self.folder_path)
            if file.endswith('.crdownload') and os.path.isfile(os.path.join(self.folder_path, file))
        ]

    def get_file_size(self, filename):
        """Return the size of a specific file in bytes. Raises error if file doesn't exist."""
        file_path = os.path.join(self.folder_path, filename)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file '{filename}' does not exist in the folder.")
        return os.path.getsize(file_path)


# Example usage:
if __name__ == "__main__":
    folder = "C:/Users/PC/Downloads/"  # Change this to your target directory
    checker = CrdownloadChecker(folder)

    print("Number of .crdownload files:", checker.count_crdownload_files())
    print("List of .crdownload files:", checker.get_crdownload_filenames())

    # Example of checking a specific file size
    try:
        file_size = checker.get_file_size("AnimePahe_One_Piece_-_247_720p_HorribleSubs.mp4.crdownload")
        print("File size:", file_size, "bytes")
    except FileNotFoundError as e:
        print(e)
print([][0])
