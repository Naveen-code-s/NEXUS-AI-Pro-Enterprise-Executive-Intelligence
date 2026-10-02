from pathlib import Path
import hashlib,re
def checksum(data): return hashlib.sha256(data).hexdigest()
def safe_name(name): return re.sub(r'[^A-Za-z0-9._ -]','_',Path(name).name) or 'upload'
