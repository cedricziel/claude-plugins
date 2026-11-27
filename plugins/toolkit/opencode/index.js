// OpenCode V2 server part for the toolkit plugin.
//
// Registers the host-neutral toolkit skills (the same non-workflow set Codex
// gets), injects the personal instructions, and runs the TDD and rebase
// reminders. Claude-only workflows and scoped agents are not registered.
import { execFile } from "node:child_process"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import { fileURLToPath } from "node:url"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const dataDir = path.join(
  process.env.XDG_STATE_HOME || path.join(os.homedir(), ".local", "state"),
  "opencode",
  "plugins",
  "toolkit",
)
try {
  fs.mkdirSync(dataDir, { recursive: true })
} catch {
  // The reflect and reminder hooks create their own state directories when needed.
}
const disabled = (name) => process.env[name] === "1"

function read(relative) {
  try {
    return fs.readFileSync(path.join(root, relative), "utf8")
  } catch {
    return ""
  }
}

function fold(lines) {
  let out = ""
  for (const line of lines) {
    if (line === "") out += "\n"
    else if (out && !out.endsWith("\n")) out += ` ${line}`
    else out += line
  }
  return out.trim()
}

function frontmatter(text) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(text)
  const fields = {}
  if (!match) return { fields, body: text }
  const lines = match[1].split(/\r?\n/)
  for (let i = 0; i < lines.length; i++) {
    const pair = /^([A-Za-z][\w-]*):\s*(.*)$/.exec(lines[i])
    if (!pair) continue
    const key = pair[1]
    const value = pair[2].trim()
    if (value === "" || /^[>|][+-]?$/.test(value)) {
      const block = []
      let j = i + 1
      while (j < lines.length) {
        const next = lines[j]
        if (next.trim() === "") {
          block.push("")
          j++
          continue
        }
        if (!/^\s+/.test(next)) break
        block.push(next)
        j++
      }
      if (block.some((line) => line.trim())) {
        i = j - 1
        const indents = block.filter((line) => line.trim()).map((line) => line.match(/^\s*/)[0].length)
        const indent = indents.length ? Math.min(...indents) : 0
        const cleaned = block.map((line) => line.slice(indent))
        fields[key] = value.startsWith("|") ? cleaned.join("\n").trim() : fold(cleaned)
        continue
      }
    }
    fields[key] = value.replace(/^["']|["']$/g, "")
  }
  return { fields, body: text.slice(match[0].length) }
}

function discoverSkills(directories) {
  const skills = []
  for (const relative of directories) {
    const directory = path.join(root, relative)
    let entries = []
    try {
      entries = fs.readdirSync(directory, { withFileTypes: true })
    } catch {
      continue
    }
    for (const entry of entries) {
      const file = path.join(directory, entry.name, "SKILL.md")
      try {
        if (!fs.statSync(file).isFile()) continue
      } catch {
        continue
      }
      const { fields, body } = frontmatter(fs.readFileSync(file, "utf8"))
      const skill = {
        id: entry.name,
        name: fields.name || entry.name,
        description: fields.description,
        path: file,
        content: body,
      }
      if (/^(true|yes|1)$/i.test(fields["disable-model-invocation"] ?? "")) skill.autoinvoke = false
      skills.push(skill)
    }
  }
  return skills
}

function run(script, payload, env = {}) {
  return new Promise((resolve) => {
    const child = execFile(
      "bash",
      [path.join(root, "scripts", script)],
      { env: { ...process.env, ...env }, timeout: 60_000, maxBuffer: 1024 * 1024 },
      (error, stdout) => resolve(error ? "" : stdout),
    )
    child.stdin?.on("error", () => {})
    child.stdin?.end(JSON.stringify(payload))
  })
}

function additionalContext(stdout) {
  try {
    return JSON.parse(stdout)?.hookSpecificOutput?.additionalContext ?? ""
  } catch {
    return ""
  }
}

function withFile(event, directory) {
  if (!["edit", "write", "patch"].includes(event.tool)) return undefined
  const input = event.input
  if (!input || typeof input !== "object") return undefined
  if (event.tool === "patch") {
    return {
      tool_name: "apply_patch",
      cwd: directory,
      tool_input: { command: input.patchText ?? "" },
    }
  }
  const file = input.path ?? input.filePath ?? input.file_path
  if (typeof file !== "string" || !file) return undefined
  return {
    tool_name: "Edit",
    cwd: directory,
    tool_input: { file_path: path.resolve(directory, file) },
  }
}

function commandPrompt(prompt, sessionID, delivery, skillID) {
  const arguments_ = prompt.text?.trim() ?? ""
  const next = {
    ...prompt,
    sessionID,
    delivery,
    text: `Load the \`${skillID}\` skill with the skill tool, then follow it.${arguments_ ? `\n\n${arguments_}` : ""}`,
  }
  for (const key of ["files", "agents", "skills"]) {
    if (Array.isArray(next[key])) next[key] = next[key].map(({ mention, ...item }) => item)
  }
  return next
}

async function register(ctx) {
  const skills = discoverSkills(["host-skills"])
  if (!skills.length) return

  await ctx.skill.transform((editor) => {
    for (const skill of skills) {
      const existing = typeof editor.get === "function" ? editor.get(skill.id) : undefined
      if (existing) continue
      try {
        editor.add(skill)
      } catch {
        // A host-provided skill with the same ID wins.
      }
    }
  })

  await ctx.command.transform((editor) => {
    for (const skill of skills) {
      try {
        editor.add({
          name: skill.id,
          description: skill.description,
          execute: async ({ sessionID, prompt, delivery }) => {
            await ctx.session.prompt(commandPrompt(prompt, sessionID, delivery, skill.id))
          },
        })
      } catch {
        // A command with the same name already exists.
      }
    }
  })
}

async function injectInstructions(ctx) {
  if (disabled("TOOLKIT_INSTRUCTIONS_DISABLE")) return
  const fleet = read("instructions/fleet-brief.md")
  const body = ["instructions/shared.md", "instructions/opencode.md"]
    .map(read)
    .filter(Boolean)
    .join("\n")
    .replaceAll("{{FLEET_BRIEF}}", fleet)
    .trim()
  if (!body) return
  const text = `<GLOBAL_INSTRUCTIONS source="toolkit plugin">
${body}
Toolkit plugin data directory for the reflect skill: ${dataDir}
</GLOBAL_INSTRUCTIONS>`
  await ctx.session.hook("context", (event) => {
    event.system.push({ type: "text", text })
  })
}

export default {
  id: "cedricziel.toolkit",
  async setup(ctx) {
    const pending = new Map()
    const remember = (sessionID, note) => {
      if (!note) return
      const notes = pending.get(sessionID) ?? []
      notes.push(note)
      pending.set(sessionID, notes)
    }

    await register(ctx)
    await injectInstructions(ctx)

    await ctx.session.hook("context", (event) => {
      const notes = pending.get(event.sessionID)
      if (!notes?.length) return
      pending.delete(event.sessionID)
      event.system.push({ type: "text", text: notes.join("\n") })
    })

    await ctx.tool.hook("execute.after", async (event) => {
      if (event.status !== "completed") return
      const payload = withFile(event, ctx.location.directory)
      if (!payload) return
      const output = await run("tdd-hook.sh", { ...payload, session_id: event.sessionID }, {
        TDD_STATE_DIR: path.join(dataDir, "tdd"),
      })
      remember(event.sessionID, additionalContext(output))
    })

    await ctx.session.hook("prompt", async (event) => {
      const output = await run(
        "rebase-hook.sh",
        { cwd: ctx.location.directory },
        { REBASE_HOOK_STATE_DIR: path.join(dataDir, "rebase") },
      )
      remember(event.sessionID, additionalContext(output))
    })
  },
}
