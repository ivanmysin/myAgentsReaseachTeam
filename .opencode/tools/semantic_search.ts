import { tool } from "@opencode-ai/plugin"
import path from "path"
import { loadEnv } from "./_env"

export default tool({
  description: "Semantic search via ChromaDB with SPECTER2 embeddings. Search abstracts, full-text chunks, or both.",
  args: {
    query: tool.schema.string().describe("Search query in natural language (English)"),
    top: tool.schema
      .number()
      .int()
      .positive()
      .optional()
      .describe("Number of results (default: 20)"),
    threshold: tool.schema
      .number()
      .optional()
      .describe("Minimum similarity threshold (default: -1.0, no filter)"),
    cluster: tool.schema
      .number()
      .int()
      .optional()
      .describe("Restrict search to cluster N"),
    collection: tool.schema
      .enum(["abstracts", "chunks", "all"])
      .optional()
      .describe("Which collection to search (default: abstracts)"),
  },
  async execute(args, context) {
    const env = loadEnv(context.worktree)
    const pythonPath = env["PYTHON_PATH"] || process.env.PYTHON_PATH || "python3"
    const scriptPath = path.join(context.worktree, ".opencode/tools/scripts/semantic_search.py")
    const cmdParts = [pythonPath, scriptPath, args.query]
    if (args.top != null) cmdParts.push("--top", String(args.top))
    if (args.threshold != null) cmdParts.push("--threshold", String(args.threshold))
    if (args.cluster != null) cmdParts.push("--cluster", String(args.cluster))
    if (args.collection) cmdParts.push("--collection", args.collection)
    const proc = Bun.spawnSync(cmdParts)
    return proc.stdout.toString()
  },
})
