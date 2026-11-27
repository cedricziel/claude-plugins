// OpenCode V2 server part for the skills plugin.
//
// Registers the plugin's tool-integration skills and a slash command per skill.
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))

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
  const skills = discoverSkills(["skills"])
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

export default {
  id: "cedricziel.skills",
  async setup(ctx) {
    await register(ctx)
  },
}
