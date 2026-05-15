import { readFileSync, existsSync } from "fs"
import path from "path"

export function loadEnv(worktree: string): Record<string, string> {
  const envPath = path.join(worktree, ".env")
  const env: Record<string, string> = {}
  if (!existsSync(envPath)) return env
  const content = readFileSync(envPath, "utf-8")
  for (const line of content.split("\n")) {
    const trimmed = line.trim()
    if (trimmed && !trimmed.startsWith("#") && trimmed.includes("=")) {
      const eqIdx = trimmed.indexOf("=")
      const key = trimmed.slice(0, eqIdx).trim()
      const value = trimmed.slice(eqIdx + 1).trim()
      env[key] = value
    }
  }
  return env
}
