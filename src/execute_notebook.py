"""Execute the completed notebook using the invoking Python environment."""
import json
import os
from pathlib import Path
import sys
import tempfile
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR','/tmp/salifort-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/salifort-cache')
with tempfile.TemporaryDirectory(prefix='salifort-kernel-') as d:
    k=Path(d)/'salifort';k.mkdir()
    (k/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Salifort Python','language':'python'}))
    km=KernelManager(kernel_name='salifort',kernel_spec_manager=KernelSpecManager(kernel_dirs=[d]))
    path=ROOT/'notebooks/Salifort_Motors_Complete.ipynb'
    nb=nbformat.read(path,as_version=4)
    NotebookClient(nb,km=km,timeout=600,resources={'metadata':{'path':str(ROOT)}}).execute()
    nbformat.write(nb,path)
    print('Executed',sum(c.cell_type=='code' for c in nb.cells),'code cells without errors.')
