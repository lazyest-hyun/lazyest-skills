from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

FIXTURE_WORKSPACE = tempfile.TemporaryDirectory()
ROOT = Path(FIXTURE_WORKSPACE.name)

class ForwardFixtures(unittest.TestCase):
    def test_heading_edit(self):
        page = ROOT / 'index.html'
        page.write_text('<main><h1>Inventory</h1><p>Inventory records</p></main>')
        before = page.read_text()
        page.write_text(before.replace('<h1>Inventory</h1>', '<h1>Stock</h1>', 1))
        self.assertEqual(page.read_text(), '<main><h1>Stock</h1><p>Inventory records</p></main>')

    def test_persistence_repro_fix_and_regression(self):
        app = ROOT / 'store.py'
        buggy = '''import json, sys
from pathlib import Path
path = Path(sys.argv[1])
items = []
if sys.argv[2] == 'create':
    items.append(json.loads(sys.argv[3]))
print(json.dumps(items))
'''
        app.write_text(buggy)
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / 'items.json')
            def run(action, item=None):
                args = [sys.executable, str(app), database, action]
                if item is not None:
                    args.append(json.dumps(item))
                return json.loads(subprocess.check_output(args, text=True))
            first = {'id': 0, 'quantity': 0}
            self.assertEqual(run('create', first), [first])
            self.assertEqual(run('read'), [])  # Reproduced loss in a fresh process.
            fixed = buggy.replace('items = []', 'items = json.loads(path.read_text()) if path.exists() else []').replace('    items.append(json.loads(sys.argv[3]))', '    items.append(json.loads(sys.argv[3]))\n    path.write_text(json.dumps(items))')
            app.write_text(fixed)
            self.assertEqual(run('create', first), [first])
            self.assertEqual(run('read'), [first])
            second = {'id': 1, 'quantity': 2}
            self.assertEqual(run('create', second), [first, second])
            self.assertEqual(run('read'), [first, second])

if __name__ == '__main__':
    unittest.main(verbosity=2)
