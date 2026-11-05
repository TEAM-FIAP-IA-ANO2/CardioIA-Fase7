from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1];out=root.parent/'CardioIA-Entrega-Final.zip'
ignore={'.git','.venv','node_modules','dist','.runtime','__pycache__','.pytest_cache'}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in root.rglob('*'):
  rel=p.relative_to(root)
  if p.is_file() and not any(x in ignore for x in rel.parts) and p.name not in {'.env','config.py'}:z.write(p,Path('CardioIA-Entrega-Final')/rel)
print(out)
