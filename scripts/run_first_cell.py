import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

# Create a temporary notebook with a single simple code cell to test the kernel
nb = nbformat.v4.new_notebook()
nb.cells = [nbformat.v4.new_code_cell("import sys\nprint(sys.executable)")]

client = NotebookClient(nb, kernel_name='diagnostico60plus', timeout=60)
try:
    client.execute()
except CellExecutionError as e:
    print('Cell execution error:', e)

out = nb.cells[0].get('outputs', [])
if not out:
    print('No output from kernel test')
else:
    for o in out:
        if o.get('output_type') == 'stream':
            print(o.get('text',''))
        elif o.get('output_type') in ('execute_result','display_data'):
            data = o.get('data',{})
            text = data.get('text/plain')
            if text:
                print(text)
        elif o.get('output_type') == 'error':
            print('Error executing test cell')
            for line in o.get('traceback',[]):
                print(line)

print('\nKernel test complete (kernel: diagnostico60plus)')
