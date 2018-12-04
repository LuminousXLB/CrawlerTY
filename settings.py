from pathlib import Path


DATA_ROOT = Path('E:/RuntimeTY')

DB_ENGINE_FILE = DATA_ROOT/'TYdata2.db'

ECHO_DATABASE_INFO = False

LOG_FILE = DATA_ROOT/'TYcrawler.log'

if not DATA_ROOT.is_dir():
    DATA_ROOT.mkdir()
