import { tool } from "@opencode-ai/plugin"
import path from "path"
import { loadEnv } from "./_env"

export default tool({
  description: "Search articles in SQLite database. Modes: keyword (full-text), sql (arbitrary SELECT), author, doi, id",
  args: {
    mode: tool.schema
      .enum(["keyword", "sql", "author", "doi", "id"])
      .describe("Search mode"),
    query: tool.schema.string().describe("Search query, SQL statement, author name, DOI, or article ID"),
    fields: tool.schema
      .string()
      .optional()
      .describe("Comma-separated fields to return (default: id,title,authors,date,doi,abstract)"),
    limit: tool.schema
      .number()
      .int()
      .positive()
      .optional()
      .describe("Maximum results (default: 20)"),
    full: tool.schema
      .boolean()
      .optional()
      .describe("Include full_text in results"),
  },
  async execute(args, context) {
    const env = loadEnv(context.worktree)
    const pythonPath = env["PYTHON_PATH"] || process.env.PYTHON_PATH || "python3"
    const scriptPath = path.join(context.worktree, ".opencode/tools/scripts/db_search.py")
    const cmdParts = [pythonPath, scriptPath, args.mode, args.query]
    if (args.fields) cmdParts.push("--fields", args.fields)
    if (args.limit != null) cmdParts.push("--limit", String(args.limit))
    if (args.full) cmdParts.push("--full")
    const proc = Bun.spawnSync(cmdParts)
    return proc.stdout.toString()
  },
})
