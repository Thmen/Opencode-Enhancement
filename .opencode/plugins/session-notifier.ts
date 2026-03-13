import { readFileSync, existsSync } from "fs"
import { join } from "path"
import { homedir } from "os"

interface NotifyConfig {
  enabled: boolean
  command: string
  message: string
  notifyOnError: boolean
  errorMessage: string
}

const DEFAULT_CONFIG: NotifyConfig = {
  enabled: true,
  command: "python notifier.py",
  message: "OpenCode 会话已完成！",
  notifyOnError: true,
  errorMessage: "OpenCode 会话出错！",
}

function loadConfig(directory: string): NotifyConfig {
  const candidates = [
    join(directory, ".opencode", "notify-config.json"),
    join(homedir(), ".config", "opencode", "notify-config.json"),
  ]

  for (const p of candidates) {
    if (existsSync(p)) {
      try {
        const raw = readFileSync(p, "utf-8")
        return { ...DEFAULT_CONFIG, ...JSON.parse(raw) }
      } catch {
        // config parse failed, try next candidate
      }
    }
  }

  return { ...DEFAULT_CONFIG }
}

export const SessionNotifier = async ({ client, $, directory }) => {
  const config = loadConfig(directory)

  await client.app.log({
    body: {
      service: "session-notifier",
      level: "info",
      message: `Session notifier loaded (enabled=${config.enabled}, command="${config.command}")`,
    },
  })

  if (!config.enabled) return {}

  return {
    event: async ({ event }) => {
      let message: string | null = null

      if (event.type === "session.idle") {
        message = config.message
      } else if (event.type === "session.error" && config.notifyOnError) {
        message = config.errorMessage
      }

      if (!message) return

      const command = config.command.replace(/\{\{message\}\}/g, message)

      try {
        await $`${{ raw: command }}`
          .env({
            OPENCODE_NOTIFY_MESSAGE: message,
            OPENCODE_SESSION_EVENT: event.type,
          })
          .quiet()
          .nothrow()
      } catch (e) {
        await client.app.log({
          body: {
            service: "session-notifier",
            level: "error",
            message: `Notification failed: ${e}`,
          },
        })
      }
    },
  }
}
