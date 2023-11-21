from pathlib import Path


cwd = Path.cwd()

if cwd.name != 'EconSim':
    raise Exception('Bad current working directory. Launch program from `main.py`')

visual_dir = cwd / 'visual'
data_dir = visual_dir / 'data'

try:
    data_dir.mkdir()

except FileExistsError:
    pass
