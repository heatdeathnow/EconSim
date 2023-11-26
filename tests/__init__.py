from pathlib import Path
from importlib import import_module
from unittest import TestLoader, TextTestRunner

loader = TestLoader()
runner = TextTestRunner()
tests_path = (Path.cwd() / __file__).parent

for directory in tests_path.iterdir():
    if not directory.is_dir() and not directory.name.startswith('__'):

        module_name = f'{tests_path.name}.{directory.with_suffix('').name}'
        module = import_module(module_name)

        suite = loader.loadTestsFromModule(module)
        runner.run(suite)
