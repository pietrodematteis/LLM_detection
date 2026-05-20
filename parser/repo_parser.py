from parser.github_loader import LocalRepoLoader
from parser.java_parser import JavaParser


class RepoParser():
    output_path = "parser_crypto.txt"

    skip_dirs = [
        ".github/",
        "docs/",
        "licenses/",
        "target/",
        "build/"
    ]
    def __init__(self, repo_path: str, output_path: str, ollama_base: str, model: str, temperature: float, timeout: float, num_ctx: int):
        self.repo_path = repo_path
        self.output_path = output_path
        self.loader = LocalRepoLoader(repo_path)

        # add here parser for every language
        self.language_parsers = {
            ".java": JavaParser(ollama_base, model, temperature, timeout, num_ctx),
        }

    def run(self):
        with open(self.output_path, "w", encoding="utf-8") as output_file:
            for path, code in self.loader.iter_files(skip_dirs=self.skip_dirs):
                language_parser = self.get_language_parser(path)

                if language_parser is None:
                    continue

                if not language_parser.should_parse_file(path):
                    continue

                print(f"\n === PARSE: {path} ===")
                language_parser.parse_file(path, code, output_file)

    def get_language_parser(self, path: str):
        for extension, language_parser in self.language_parsers.items():
            if path.endswith(extension):
                return language_parser
        return None
