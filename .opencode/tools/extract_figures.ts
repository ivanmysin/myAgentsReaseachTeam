import { tool } from "@opencode-ai/plugin"
import path from "path"
import { loadEnv } from "./_env"

export default tool({
  description: "Extract figures from an article PDF. Saves images to a directory.",
  args: {
    id: tool.schema
      .number()
      .int()
      .positive()
      .describe("Article ID"),
    output: tool.schema
      .string()
      .optional()
      .describe("Output directory (default: output/figures/<id>/)"),
    minSize: tool.schema
      .number()
      .int()
      .positive()
      .optional()
      .describe("Minimum image dimension in pixels (default: 100)"),
  },
  async execute(args, context) {
    const env = loadEnv(context.worktree)
    const pythonPath = env["PYTHON_PATH"] || process.env.PYTHON_PATH || "python3"
    const scriptPath = path.join(context.worktree, ".opencode/tools/scripts/extract_figures.py")
    const cmdParts = [pythonPath, scriptPath, String(args.id)]
    if (args.output) cmdParts.push("--output", args.output)
    if (args.minSize != null) cmdParts.push("--min-size", String(args.minSize))
    const proc = Bun.spawnSync(cmdParts)
    return proc.stdout.toString()
  },
})
