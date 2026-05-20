from abc import ABC, abstractmethod

class LanguageParser(ABC):
    extensions : tuple[str, ...] = ()

    def should_parse_file(self, path: str)  -> bool:
        return True

    @abstractmethod
    def parse_file(self, path: str, code: bytes, output_file):
        pass