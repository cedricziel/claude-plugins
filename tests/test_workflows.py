import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parent.parent / "plugins" / "toolkit" / "workflows"


@unittest.skipUnless(shutil.which("node"), "node not installed")
class WorkflowSyntaxTest(unittest.TestCase):
    def test_each_workflow_parses_as_async_module_body(self):
        for js in sorted(WORKFLOWS.glob("*.js")):
            src = js.read_text()
            head, _, body = src.partition("\n}\n")  # split after `export const meta = {...}`
            wrapped = head + "\n}\n" + "export default async function run(args, agent, parallel, pipeline, phase, log, budget, workflow) {\n" + body + "\n}\n"
            with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
                f.write(wrapped)
            r = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"{js.name}: {r.stderr}")


if __name__ == "__main__":
    unittest.main()
