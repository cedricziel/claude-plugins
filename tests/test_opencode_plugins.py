import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NODE = shutil.which("node")

HARNESS = r"""
import { pathToFileURL } from "node:url"

const state = { skills: [], commands: [], hooks: [], prompts: [], system: [] }
const list = (data) => ({ location: { directory: process.cwd() }, data })
const ctx = {
  location: { directory: process.cwd() },
  skill: {
    list: async () => list([]),
    transform: async (fn) => {
      fn({ list: () => [], get: () => undefined, add: (skill) => state.skills.push(skill), update() {}, remove() {} })
      return { dispose() {} }
    },
  },
  command: {
    list: async () => list([]),
    transform: async (fn) => {
      fn({ add: (command) => state.commands.push(command) })
      return { dispose() {} }
    },
  },
  session: {
    hook: async (name, callback) => {
      state.hooks.push([name, callback])
      return { dispose() {} }
    },
    prompt: async (prompt) => state.prompts.push(prompt),
  },
  tool: {
    hook: async (name, callback) => {
      state.hooks.push([name, callback])
      return { dispose() {} }
    },
  },
}

const plugin = (await import(pathToFileURL(process.argv[1]))).default
await plugin.setup(ctx)
for (const [name, callback] of state.hooks) {
  if (name === "context") await callback({ sessionID: "s1", system: state.system })
}
if (state.commands[0]) {
  await state.commands[0].execute({ sessionID: "s1", prompt: { text: "arg" }, delivery: "steer" })
}
console.log(JSON.stringify({
  id: plugin.id,
  skills: state.skills.map((skill) => skill.id),
  commands: state.commands.map((command) => command.name),
  hooks: state.hooks.map(([name]) => name),
  system: state.system.map((part) => part.text).join("\n"),
  prompts: state.prompts,
}))
"""


@unittest.skipUnless(NODE, "node is required to load the OpenCode plugins")
class OpenCodePluginTest(unittest.TestCase):
    def load(self, name):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        result = subprocess.run(
            [NODE, "--input-type=module", "-e", HARNESS, str(ROOT / "plugins" / name / "opencode" / "index.js")],
            cwd=self.tmp,
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "HOME": str(self.tmp),
                "XDG_STATE_HOME": str(self.tmp / "state"),
            },
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_common_registers_skills_commands_and_instructions(self):
        data = self.load("common")
        self.assertEqual(data["id"], "cedricziel.common")
        for skill in ("unslop", "code-comments", "test-strategy"):
            self.assertIn(skill, data["skills"])
        self.assertEqual(data["commands"], data["skills"])
        self.assertIn("Choose the simplest sound solution", data["system"])
        self.assertIn("OpenCode's supported tools", data["system"])
        self.assertEqual(data["hooks"].count("context"), 1)
        self.assertIn("execute.after", data["hooks"])
        self.assertIn("Load the `", data["prompts"][0]["text"])
        self.assertIn("arg", data["prompts"][0]["text"])

    def test_oss_registers_skills_and_instructions(self):
        data = self.load("oss")
        self.assertEqual(data["id"], "cedricziel.oss")
        self.assertIn("commit-discipline", data["skills"])
        self.assertIn("technical-writing", data["skills"])
        self.assertIn("semantic commits", data["system"])
        self.assertNotIn("execute.after", data["hooks"])

    def test_skills_registers_only_skills(self):
        data = self.load("skills")
        self.assertEqual(data["id"], "cedricziel.skills")
        for skill in ("coderabbit", "forgejo-cli", "pangolin-api", "dashboarding", "openspec-doctor"):
            self.assertIn(skill, data["skills"])
        self.assertEqual(data["system"], "")
        self.assertEqual(data["hooks"], [])

    def test_toolkit_registers_host_skills_and_reminders(self):
        data = self.load("toolkit")
        self.assertEqual(data["id"], "cedricziel.toolkit")
        for skill in ("new-repository", "project-review", "reflect", "signaldb-observe"):
            self.assertIn(skill, data["skills"])
        self.assertIn("Caveman Compression", data["system"])
        self.assertIn("Toolkit plugin data directory for the reflect skill", data["system"])
        self.assertIn(str(self.tmp / "state" / "opencode" / "plugins" / "toolkit"), data["system"])
        self.assertIn("prompt", data["hooks"])
        self.assertIn("execute.after", data["hooks"])


if __name__ == "__main__":
    unittest.main()
