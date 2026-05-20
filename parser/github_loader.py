import os

class LocalRepoLoader:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def iter_files(self, extension=None, skip_dirs=None):
        if skip_dirs is None:
            skip_dirs = []

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [
                d for d in dirs
                if not any(skip in os.path.join(root, d) for skip in skip_dirs)
            ]

            for file in files:
                if extension and not file.endswith(extension):
                    continue

                path = os.path.join(root, file)

                try:
                    with open(path, "rb") as f:
                        yield path, f.read()
                except Exception as e:
                    print(f"[ERROR] {path}: {e}")