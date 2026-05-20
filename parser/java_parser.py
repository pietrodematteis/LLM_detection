from typing import TextIO

from tree_sitter import Language, Parser
import tree_sitter_java as tsjava

from engine.detector import detect_crypto_report
from parser.language_parser import LanguageParser

class JavaParser(LanguageParser):
    extensions = (".java",)

    def __init__(self, ollama_base, model, temperature, timeout, num_ctx):

        # Ollama
        self.ollama_base = ollama_base
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.num_ctx = num_ctx
        # JCA
        self.crypto_keywords_java_security = [
            "MessageDigest.getInstance",
            "Signature.getInstance",
            "KeyFactory.getInstance",
            "KeyPairGenerator.getInstance",
            "AlgorithmParameters.getInstance",
            "AlgorithmParameterGenerator.getInstance",
            "SecureRandom.getInstance",
            "SecureRandom.getInstanceStrong",
            "new SecureRandom",
        ]

        self.crypto_keywords_javax_crypto = [
            "Cipher.getInstance",
            "Mac.getInstance",
            "KeyAgreement.getInstance",
            "KeyGenerator.getInstance",
            "SecretKeyFactory.getInstance",
        ]

        self.crypto_imports = ["java.security", "javax.crypto"]

        # set parser
        java_language = Language(tsjava.language())
        self.parser = Parser(java_language)

    def should_parse_file(self, path: str) -> bool:
        return "/src/main/java/" in path

    def parse_file(self, path: str, code: bytes, output_file: TextIO) -> None:
        tree = self.parser.parse(code)
        root = tree.root_node

        imports = self.get_imports(root, code)

        if self.has_crypto_imports(imports, self.crypto_imports):
            constants = self.collect_static_final_constants(root, code)
            seen_methods = set()
            self.find_method_calls(root, constants, code, seen_methods, path, output_file)

    def find_parent_methods(self, node):
        while node is not None:
            if node.type == "method_declaration":
                return node
            node = node.parent
        return None

    def get_imports(self, node, code):
        imports = []

        if node.type == "import_declaration":
            text = code[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")
            imports.append(text)

        for child in node.children:
            results = self.get_imports(child, code)
            if results:
                imports.extend(results)

        return imports

    def has_crypto_imports(self, imports, crypto_imports):
        for imp in imports:
            if any(keyword in imp for keyword in crypto_imports):
                print("found crypto import:", imp)
                return True
        return False

    def print_chunk(self, node, code, context_lines=3):
        start_line = node.start_point[0]
        end_line = node.end_point[0]

        lines = code.decode("utf-8", errors="ignore").split("\n")

        start = max(0, start_line - context_lines)
        end = min(len(lines), end_line + context_lines + 1)

        print("\n--- CHUNK ---")
        print("\n".join(lines[start:end]))

    def find_method_calls(self, node, constants, code, seen_methods, path, file):
        if node.type == "method_invocation":
            text = code[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

            all_keywords = self.crypto_keywords_java_security + self.crypto_keywords_javax_crypto

            # for debug
            #all_keywords = ["crypto.keyGenerator"]
            if any(k in text for k in all_keywords):
                method_node = self.find_parent_methods(node)

                if method_node:
                    print("EXTRA CALL:")
                    print(text)
                    key = (method_node.start_byte, method_node.end_byte)
                    if key not in seen_methods:
                        seen_methods.add(key)

                        print(f"\nFILE: {path}")
                        print("CALL:", text)
                        print("KEY:", key)

                        method_text = self.get_method_with_constants(method_node, constants, code)

                        print("METHOD:")
                        print(method_text)
                        print("=" * 80)
                        file.write(f"\nFILE: {path}\n")
                        file.write(f"CALL: {text}\n")
                        file.write(f"KEY: {key}\n")
                        file.write("METHOD:\n")
                        file.write(method_text + "\n")
                        file.write("." * 80 + "\n")

                        llm_output = detect_crypto_report(
                            input_path=path,
                            code=method_text,
                            ollama_base=self.ollama_base,
                            model=self.model,
                            temperature=self.temperature,
                            timeout=self.timeout,
                            num_ctx=self.num_ctx
                        )

                        if isinstance(llm_output, list):
                            llm_output = "\n".join(llm_output)
                        file.write(f"\nLLM: {llm_output}\n")
                        file.write("=" * 80 + "\n")

        for child in node.children:
            self.find_method_calls(child, constants, code, seen_methods, path, file)

    def collect_static_final_constants(self, node, code, constants=None):
        if constants is None:
            constants = {}

        if node.type == "field_declaration":
            modifiers_text = ""

            for child in node.children:
                if child.type == "modifiers":
                    modifiers_text = code[child.start_byte:child.end_byte].decode("utf-8")
                    break

            if "static" in modifiers_text and "final" in modifiers_text:
                for child in node.children:
                    if child.type == "variable_declarator":
                        name_node = child.child_by_field_name("name")
                        value_node = child.child_by_field_name("value")

                        if name_node and value_node:
                            name = code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                            value = code[value_node.start_byte:value_node.end_byte].decode("utf-8")
                            constants[name] = value

        for child in node.children:
            self.collect_static_final_constants(child, code, constants)

        return constants

    def get_method_with_constants(self, method_node, constants, code):
        method_text = code[method_node.start_byte:method_node.end_byte].decode("utf-8")
        replacements = []

        def visit(node):
            if node.type == "identifier":
                ident_text = code[node.start_byte:node.end_byte].decode("utf-8")
                if ident_text in constants:
                    rel_start = node.start_byte - method_node.start_byte
                    rel_end = node.end_byte - method_node.start_byte

                    # for debug
                    resolved_value = constants[ident_text]
                    original_fragment = method_text[rel_start:rel_end]
                    print(f"DEBUG replace: {original_fragment} -> {resolved_value} [{rel_start}:{rel_end}]")
                    #

                    replacements.append((rel_start, rel_end, constants[ident_text]))

            for child in node.children:
                visit(child)

        visit(method_node)

        for start, end, value in sorted(replacements, reverse=True):
            method_text = method_text[:start] + value + method_text[end:]

        return method_text
