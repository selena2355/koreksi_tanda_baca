import os


def remove_file_if_exists(folder_path, filename, return_path=False):
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass
    return file_path if return_path else None


def write_text_file(folder_path, filename, content):
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "w", encoding="utf-8") as handle:
        handle.write(content or "")
    return file_path


def read_text_file(folder_path, filename):
    file_path = os.path.join(folder_path, filename)
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r", encoding="utf-8") as handle:
        return handle.read()
