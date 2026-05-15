import { tool } from "@opencode-ai/plugin"
import path from "path"
import { loadEnv } from "./_env"

export default tool({
  description: "Read full text of an article from the database. Supports sections, chunks, summary, and full text output.",
  args: {
    id: tool.schema
      .number()
      .int()
      .positive()
      .describe("Article ID"),
    section: tool.schema
      .enum(["intro", "methods", "results", "discussion", "all"])
      .optional()
      .describe("Extract a specific section (heuristic)"),
    chunk: tool.schema
      .number()
      .int()
      .optional()
      .describe("Return specific chunk number (0-indexed)"),
    chunks: tool.schema
      .boolean()
      .optional()
      .describe("Show number of chunks and their sizes"),
    chunkSize: tool.schema
      .number()
      .int()
      .positive()
      .optional()
      .describe("Words per chunk (default: 3000)"),
    summary: tool.schema
      .boolean()
      .optional()
      .describe("Show metadata + first 500 words"),
    full: tool.schema
      .boolean()
      .optional()
      .describe("Show full text (caution: ~15K tokens)"),
  },
  async execute(args, context) {
    const env = loadEnv(context.worktree)
    const pythonPath = env["PYTHON_PATH"] || process.env.PYTHON_PATH || "python3"
    const scriptPath = path.join(context.worktree, ".opencode/tools/scripts/read_article.py")
    const cmdParts = [pythonPath, scriptPath, String(args.id)]
    if (args.section) cmdParts.push("--section", args.section)
    if (args.chunk != null) cmdParts.push("--chunk", String(args.chunk))
    if (args.chunks) cmdParts.push("--chunks")
    if (args.chunkSize != null) cmdParts.push("--chunk-size", String(args.chunkSize))
    if (args.summary) cmdParts.push("--summary")
    if (args.full) cmdParts.push("--full")
    const proc = Bun.spawnSync(cmdParts)
    return proc.stdout.toString()
  },
})
