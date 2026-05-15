import { tool } from "@opencode-ai/plugin"
import path from "path"
import { loadEnv } from "./_env"

export default tool({
  description: "Browse article clusters. List all clusters, show articles in a cluster, or find clusters by keyword.",
  args: {
    mode: tool.schema
      .enum(["list", "show", "find"])
      .describe("Browse mode: list all clusters, show specific cluster, or find by keywords"),
    argument: tool.schema
      .string()
      .optional()
      .describe("Cluster number (for show) or search query (for find)"),
  },
  async execute(args, context) {
    const env = loadEnv(context.worktree)
    const pythonPath = env["PYTHON_PATH"] || process.env.PYTHON_PATH || "python3"
    const scriptPath = path.join(context.worktree, ".opencode/tools/scripts/cluster_browse.py")
    const cmdParts = [pythonPath, scriptPath, args.mode]
    if (args.argument) cmdParts.push(args.argument)
    const proc = Bun.spawnSync(cmdParts)
    return proc.stdout.toString()
  },
})
