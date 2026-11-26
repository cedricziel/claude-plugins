// OpenCode V2 server part for the oss plugin.
//
// Registers the plugin's skills and a slash command per skill, and injects the
// shared engineering instructions before each model step.
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const disabled = (name) => process.env[name] === "1"

function read(relative) {
  try {
    return fs.readFileSync(path.join(root, relative), "utf8")
  } catch {
    return ""
  }
}

function frontmatter(text) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(text)
  const fields = {}
  for (const line of match?.[1]?.split(/\r?\n/) ?? []) {
    const pair = /^([A-Za-z][\w-]*):\s*(.+)$/.exec(line)
    if (pair) fields[pair[1]] = pair[2].trim().replace(/^["']|["']$/g, "")
  }
  return { fields, body: match ? text.slice(match[0].length) : text }
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
      skills.push({
        id: entry.name,
        name: fields.name || entry.name,
        description: fields.description,
        path: file,
        content: body,
      })
    }
  }
  return skills
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
            const arguments_ = prompt.text?.trim() ?? ""
            await ctx.session.prompt({
              sessionID,
              delivery,
              text: `Load the \`${skill.id}\` skill with the skill tool, then follow it.${arguments_ ? `\n\n${arguments_}` : ""}`,
            })
          },
        })
      } catch {
        // A command with the same name already exists.
      }
    }
  })
}

async function injectInstructions(ctx) {
  if (disabled("OSS_INSTRUCTIONS_DISABLE")) return
  const body = ["instructions/shared.md", "instructions/opencode.md"].map(read).filter(Boolean).join("\n").trim()
  if (!body) return
  const text = `<GLOBAL_INSTRUCTIONS source="oss plugin">\n${body}\n</GLOBAL_INSTRUCTIONS>`
  await ctx.session.hook("context", (event) => {
    event.system.push({ type: "text", text })
  })
}

export default {
  id: "cedricziel.oss",
  async setup(ctx) {
    await register(ctx)
    await injectInstructions(ctx)
  },
}
