[Home](../README.md) / [Platforms and integrations](README.md) / Platforms and integrations

# Platforms and integrations

> Choose where to run Claude Code and what to connect it to. Compare the CLI, Desktop, VS Code, JetBrains, web, and integrations like Chrome, Slack, and CI/CD.

Claude Code runs the same underlying engine everywhere, but each surface is tuned for a different way of working. This page helps you pick the right platform for your workflow and connect the tools you already use.

## Where to run Claude Code

Choose a platform based on how you like to work and where your project lives.

| Platform                          | Best for                                                                                           | What you get                                                                                                                                         |
| :-------------------------------- | :------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| [CLI](../Getting started/03-Quickstart.md)             | Terminal workflows, scripting, remote servers                                                      | Full feature set, [Agent SDK](../23-RunClaudeCodeprogrammatically.md), third-party providers                                                                                   |
| [Desktop](../14-UseClaudeCodeDesktop.md)            | Visual review, parallel sessions, managed setup                                                    | Diff viewer, app preview, [computer use](../14-UseClaudeCodeDesktop.md#let-claude-use-your-computer) and [Dispatch](../14-UseClaudeCodeDesktop.md#sessions-from-dispatch) on Pro and Max |
| [VS Code](06-UseClaudeCodeinVSCode.md)            | Working inside VS Code without switching to a terminal                                             | Inline diffs, integrated terminal, file context                                                                                                      |
| [JetBrains](02-JetBrainsIDEs.md)        | Working inside IntelliJ, PyCharm, WebStorm, or other JetBrains IDEs                                | Diff viewer, selection sharing, terminal session                                                                                                     |
| [Web](../08-ClaudeCodeontheweb.md) | Long-running tasks that don't need much steering, or work that should continue when you're offline | Anthropic-managed cloud, continues after you disconnect                                                                                              |

The CLI is the most complete surface for terminal-native work: scripting, third-party providers, and the Agent SDK are CLI-only. Desktop and the IDE extensions trade some CLI-only features for visual review and tighter editor integration. The web runs in Anthropic's cloud, so tasks keep going after you disconnect.

You can mix surfaces on the same project. Configuration, project memory, and MCP servers are shared across the local surfaces.

## Connect your tools

Integrations let Claude work with services outside your codebase.

| Integration                          | What it does                                       | Use it for                                                       |
| :----------------------------------- | :------------------------------------------------- | :--------------------------------------------------------------- |
| [Chrome](01-UseClaudeCodewithChrome(beta).md)                 | Controls your browser with your logged-in sessions | Testing web apps, filling forms, automating sites without an API |
| [GitHub Actions](../20-ClaudeCodeGitHubActions.md) | Runs Claude in your CI pipeline                    | Automated PR reviews, issue triage, scheduled maintenance        |
| [GitLab CI/CD](../21-ClaudeCodeGitLabCICD.md)     | Same as GitHub Actions for GitLab                  | CI-driven automation on GitLab                                   |
| [Code Review](../10-CodeReview.md)       | Reviews every PR automatically                     | Catching bugs before human review                                |
| [Slack](05-ClaudeCodeinSlack.md)                   | Responds to `@Claude` mentions in your channels    | Turning bug reports into pull requests from team chat            |

For integrations not listed here, [MCP servers](../30-ConnectClaudeCodetotoolsviaMCP.md) and [connectors](../14-UseClaudeCodeDesktop.md#connect-external-tools) let you connect almost anything: Linear, Notion, Google Drive, or your own internal APIs.

## Work when you are away from your terminal

Claude Code offers several ways to work when you're not at your terminal. They differ in what triggers the work, where Claude runs, and how much you need to set up.

|                                                | Trigger                                                                                        | Claude runs on                                                                                                   | Setup                                                                                                                                | Best for                                                      |
| :--------------------------------------------- | :--------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------ |
| [Dispatch](../14-UseClaudeCodeDesktop.md#sessions-from-dispatch) | Message a task from the Claude mobile app                                                      | Your machine (Desktop)                                                                                           | [Pair the mobile app with Desktop](https://support.claude.com/en/articles/13947068)                                                  | Delegating work while you're away, minimal setup              |
| [Remote Control](04-ContinuelocalsessionsfromanydevicewithRemoteControl.md)           | Drive a running session from [claude.ai/code](https://claude.ai/code) or the Claude mobile app | Your machine (CLI or VS Code)                                                                                    | Run `claude remote-control`                                                                                                          | Steering in-progress work from another device                 |
| [Channels](../05-Pusheventsintoarunningsessionwithchannels.md)                       | Push events from a chat app like Telegram or Discord, or your own server                       | Your machine (CLI)                                                                                               | [Install a channel plugin](../05-Pusheventsintoarunningsessionwithchannels.md#quickstart) or [build your own](../06-Channelsreference.md)                                      | Reacting to external events like CI failures or chat messages |
| [Slack](05-ClaudeCodeinSlack.md)                             | Mention `@Claude` in a team channel                                                            | Anthropic cloud                                                                                                  | [Install the Slack app](05-ClaudeCodeinSlack.md#setting-up-claude-code-in-slack) with [Claude Code on the web](../08-ClaudeCodeontheweb.md) enabled | PRs and reviews from team chat                                |
| [Scheduled tasks](../41-Runpromptsonaschedule.md)         | Set a schedule                                                                                 | [CLI](../41-Runpromptsonaschedule.md), [Desktop](../14-UseClaudeCodeDesktop.md#schedule-recurring-tasks), or [cloud](../54-Scheduletasksontheweb.md) | Pick a frequency                                                                                                                     | Recurring automation like daily reviews                       |

If you're not sure where to start, [install the CLI](../Getting started/03-Quickstart.md) and run it in a project directory. If you'd rather not use a terminal, [Desktop](../15-Getstartedwiththedesktopapp.md) gives you the same engine with a graphical interface.

## Related resources

### Platforms

* [CLI quickstart](../Getting started/03-Quickstart.md): install and run your first command in the terminal
* [Desktop](../14-UseClaudeCodeDesktop.md): visual diff review, parallel sessions, computer use, and Dispatch
* [VS Code](06-UseClaudeCodeinVSCode.md): the Claude Code extension inside your editor
* [JetBrains](02-JetBrainsIDEs.md): the extension for IntelliJ, PyCharm, and other JetBrains IDEs
* [Claude Code on the web](../08-ClaudeCodeontheweb.md): cloud sessions that keep running when you disconnect

### Integrations

* [Chrome](01-UseClaudeCodewithChrome(beta).md): automate browser tasks with your logged-in sessions
* [GitHub Actions](../20-ClaudeCodeGitHubActions.md): run Claude in your CI pipeline
* [GitLab CI/CD](../21-ClaudeCodeGitLabCICD.md): the same for GitLab
* [Code Review](../10-CodeReview.md): automatic review on every pull request
* [Slack](05-ClaudeCodeinSlack.md): send tasks from team chat, get PRs back

### Remote access

* [Dispatch](../14-UseClaudeCodeDesktop.md#sessions-from-dispatch): message a task from your phone and it can spawn a Desktop session
* [Remote Control](04-ContinuelocalsessionsfromanydevicewithRemoteControl.md): drive a running session from your phone or browser
* [Channels](../05-Pusheventsintoarunningsessionwithchannels.md): push events from chat apps or your own servers into a session
* [Scheduled tasks](../41-Runpromptsonaschedule.md): run prompts on a recurring schedule
