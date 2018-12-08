from pathlib import Path


DATA_ROOT = Path('RuntimeTY')

DB_ENGINE_FILE = DATA_ROOT/'TYdata3.db'

ECHO_DATABASE_INFO = True

LOG_FILE = DATA_ROOT/'TYcrawler.log'

if not DATA_ROOT.is_dir():
    DATA_ROOT.mkdir()
