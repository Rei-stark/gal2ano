import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
import sys

DATA_DIR = r'C:\Users\Reinaldo\OneDrive\Rei\IMAGE TI\DataScience\Projeto Aplicado\diagnostico_60mais\data'

p = r'C:\Users\Reinaldo\OneDrive\Rei\IMAGE TI\DataScience\Projeto Aplicado\diagnostico_60mais\notebooks\Diagnostico_60mais_PA.ipynb'
nb = nbformat.read(p, as_version=4)
# find first non-empty code cell
src = None
for cell in nb.cells:
    if cell.cell_type == 'code' and cell.source.strip():
        src = cell.source
        break
if not src:
    print('Nenhuma célula de código encontrada')
    sys.exit(0)

test_nb = nbformat.v4.new_notebook()
test_nb.cells = [nbformat.v4.new_code_cell(src)]
# execute the single cell in a fresh notebook using the project kernel
# prepend a chdir to DATA_DIR so relative file paths resolve
prepended = f"import os\nos.chdir(r'{DATA_DIR}')\n\n" + src
test_nb = nbformat.v4.new_notebook()
test_nb.cells = [nbformat.v4.new_code_cell(prepended)]
client = NotebookClient(test_nb, kernel_name='diagnostico60plus', timeout=600)
try:
    client.execute()
except CellExecutionError as e:
    print('Erro durante a execução da célula:', e)

outputs = test_nb.cells[0].get('outputs', [])
if not outputs:
    print('Sem saída; verifique erros ou o caminho do arquivo')
else:
    for out in outputs:
        typ = out.get('output_type')
        if typ == 'stream':
            print(out.get('text',''))
        elif typ in ('execute_result', 'display_data'):
            data = out.get('data', {})
            text = data.get('text/plain') or data.get('text/html')
            if text:
                print(text)
        elif typ == 'error':
            print('TRACEBACK:')
            for line in out.get('traceback', []):
                print(line)

print('\n--- execução finalizada ---')
