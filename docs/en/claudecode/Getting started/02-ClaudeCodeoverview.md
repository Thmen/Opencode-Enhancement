[Home](../README.md) / [Getting started](README.md) / Claude Code overview

# Claude Code overview

> Claude Code is an agentic coding tool that reads your codebase, edits files, runs commands, and integrates with your development tools. Available in your terminal, IDE, desktop app, and browser.

Claude Code is an AI-powered coding assistant that helps you build features, fix bugs, and automate development tasks. It understands your entire codebase and can work across multiple files and tools to get things done.

## Get started

Choose your environment to get started. Most surfaces require a [Claude subscription](https://claude.com/pricing?utm_source=claude_code\&utm_medium=docs\&utm_content=overview_pricing) or [Anthropic Console](https://console.anthropic.com/) account. The Terminal CLI and VS Code also support [third-party providers](../50-Enterprisedeploymentoverview.md).

#### Terminal
The full-featured CLI for working with Claude Code directly in your terminal. Edit files, run commands, and manage your entire project from the command line.

To install Claude Code, use one of the following methods:

#### Native Install (Recommended)
    **macOS, Linux, WSL:**

    ```bash
        curl -fsSL https://claude.ai/install.sh | bash
        ```

    **Windows PowerShell:**

    ```powershell
        irm https://claude.ai/install.ps1 | iex
        ```

    **Windows CMD:**

    ```batch
        curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
        ```

    **Windows requires [Git for Windows](https://git-scm.com/downloads/win).** Install it first if you don't have it.

**Info:**
      Native installations automatically update in the background to keep you on the latest version.

#### Homebrew
    ```bash
        brew install --cask claude-code
        ```

**Info:**
      Homebrew installations do not auto-update. Run `brew upgrade claude-code` periodically to get the latest features and security fixes.

#### WinGet
    ```powershell
        winget install Anthropic.ClaudeCode
        ```

**Info:**
      WinGet installations do not auto-update. Run `winget upgrade Anthropic.ClaudeCode` periodically to get the latest features and security fixes.

Then start Claude Code in any project:

```bash
    cd your-project
    claude
    ```

You'll be prompted to log in on first use. That's it! [Continue with the Quickstart →](03-Quickstart.md)

**Tip:**
  See [advanced setup](../45-Advancedsetup.md) for installation options, manual updates, or uninstallation instructions. Visit [troubleshooting](../52-Troubleshooting.md) if you hit issues.

#### VS Code
The VS Code extension provides inline diffs, @-mentions, plan review, and conversation history directly in your editor.

* [Install for VS Code](vscode:extension/anthropic.claude-code)
* [Install for Cursor](cursor:extension/anthropic.claude-code)

Or search for "Claude Code" in the Extensions view (`Cmd+Shift+X` on Mac, `Ctrl+Shift+X` on Windows/Linux). After installing, open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`), type "Claude Code", and select **Open in New Tab**.

[Get started with VS Code →](../Platforms and integrations/06-UseClaudeCodeinVSCode.md#get-started)

#### Desktop app
A standalone app for running Claude Code outside your IDE or terminal. Review diffs visually, run multiple sessions side by side, schedule recurring tasks, and kick off cloud sessions.

Download and install:

* [macOS](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code\&utm_medium=docs) (Intel and Apple Silicon)
* [Windows](https://claude.ai/api/desktop/win32/x64/exe/latest/redirect?utm_source=claude_code\&utm_medium=docs) (x64)
* [Windows ARM64](https://claude.ai/api/desktop/win32/arm64/exe/latest/redirect?utm_source=claude_code\&utm_medium=docs) (remote sessions only)

After installing, launch Claude, sign in, and click the **Code** tab to start coding. A [paid subscription](https://claude.com/pricing?utm_source=claude_code\&utm_medium=docs\&utm_content=overview_desktop_pricing) is required.

[Learn more about the desktop app →](../15-Getstartedwiththedesktopapp.md)

#### Web
Run Claude Code in your browser with no local setup. Kick off long-running tasks and check back when they're done, work on repos you don't have locally, or run multiple tasks in parallel. Available on desktop browsers and the Claude iOS app.

Start coding at [claude.ai/code](https://claude.ai/code).

[Get started on the web →](../08-ClaudeCodeontheweb.md#getting-started)

#### JetBrains
A plugin for IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs with interactive diff viewing and selection context sharing.

Install the [Claude Code plugin](https://plugins.jetbrains.com/plugin/27310-claude-code-beta-) from the JetBrains Marketplace and restart your IDE.

[Get started with JetBrains →](../Platforms and integrations/02-JetBrainsIDEs.md)

## What you can do

Here are some of the ways you can use Claude Code:

### Automate the work you keep putting off
Claude Code handles the tedious tasks that eat up your day: writing tests for untested code, fixing lint errors across a project, resolving merge conflicts, updating dependencies, and writing release notes.

```bash
    claude "write tests for the auth module, run them, and fix any failures"
    ```

### Build features and fix bugs
Describe what you want in plain language. Claude Code plans the approach, writes the code across multiple files, and verifies it works.

For bugs, paste an error message or describe the symptom. Claude Code traces the issue through your codebase, identifies the root cause, and implements a fix. See [common workflows](../Use Claude Code/02-Commonworkflows.md) for more examples.

### Create commits and pull requests
Claude Code works directly with git. It stages changes, writes commit messages, creates branches, and opens pull requests.

```bash
    claude "commit my changes with a descriptive message"
    ```

In CI, you can automate code review and issue triage with [GitHub Actions](../20-ClaudeCodeGitHubActions.md) or [GitLab CI/CD](../21-ClaudeCodeGitLabCICD.md).

### Connect your tools with MCP
The [Model Context Protocol (MCP)](../30-ConnectClaudeCodetotoolsviaMCP.md) is an open standard for connecting AI tools to external data sources. With MCP, Claude Code can read your design docs in Google Drive, update tickets in Jira, pull data from Slack, or use your own custom tooling.

### Customize with instructions, skills, and hooks
[`CLAUDE.md`](../Use Claude Code/03-HowClauderemembersyourproject.md) is a markdown file you add to your project root that Claude Code reads at the start of every session. Use it to set coding standards, architecture decisions, preferred libraries, and review checklists. Claude also builds [auto memory](../Use Claude Code/03-HowClauderemembersyourproject.md#auto-memory) as it works, saving learnings like build commands and debugging insights across sessions without you writing anything.

Create [custom commands](../46-ExtendClaudewithskills.md) to package repeatable workflows your team can share, like `/review-pr` or `/deploy-staging`.

[Hooks](../24-Hooksreference.md) let you run shell commands before or after Claude Code actions, like auto-formatting after every file edit or running lint before a commit.

### Run agent teams and build custom agents
Spawn [multiple Claude Code agents](../48-Createcustomsubagents.md) that work on different parts of a task simultaneously. A lead agent coordinates the work, assigns subtasks, and merges results.

For fully custom workflows, the [Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) lets you build your own agents powered by Claude Code's tools and capabilities, with full control over orchestration, tool access, and permissions.

### Pipe, script, and automate with the CLI
Claude Code is composable and follows the Unix philosophy. Pipe logs into it, run it in CI, or chain it with other tools:

```bash
    # Analyze recent log output
    tail -200 app.log | claude -p "Slack me if you see any anomalies"

    # Automate translations in CI
    claude -p "translate new strings into French and raise a PR for review"

    # Bulk operations across files
    git diff main --name-only | claude -p "review these changed files for security issues"
    ```

See the [CLI reference](../09-CLIreference.md) for the full set of commands and flags.

### Schedule recurring tasks
Run Claude on a schedule to automate work that repeats: morning PR reviews, overnight CI failure analysis, weekly dependency audits, or syncing docs after PRs merge.

* [Cloud scheduled tasks](../54-Scheduletasksontheweb.md) run on Anthropic-managed infrastructure, so they keep running even when your computer is off. Create them from the web, the Desktop app, or by running `/schedule` in the CLI.
* [Desktop scheduled tasks](../14-UseClaudeCodeDesktop.md#schedule-recurring-tasks) run on your machine, with direct access to your local files and tools
* [`/loop`](../41-Runpromptsonaschedule.md) repeats a prompt within a CLI session for quick polling

### Work from anywhere
Sessions aren't tied to a single surface. Move work between environments as your context changes:

* Step away from your desk and keep working from your phone or any browser with [Remote Control](../Platforms and integrations/04-ContinuelocalsessionsfromanydevicewithRemoteControl.md)
* Message [Dispatch](../14-UseClaudeCodeDesktop.md#sessions-from-dispatch) a task from your phone and open the Desktop session it creates
* Kick off a long-running task on the [web](../08-ClaudeCodeontheweb.md) or [iOS app](https://apps.apple.com/app/claude-by-anthropic/id6473753684), then pull it into your terminal with `/teleport`
* Hand off a terminal session to the [Desktop app](../14-UseClaudeCodeDesktop.md) with `/desktop` for visual diff review
* Route tasks from team chat: mention `@Claude` in [Slack](../Platforms and integrations/05-ClaudeCodeinSlack.md) with a bug report and get a pull request back

## Use Claude Code everywhere

Each surface connects to the same underlying Claude Code engine, so your CLAUDE.md files, settings, and MCP servers work across all of them.

Beyond the [Terminal](03-Quickstart.md), [VS Code](../Platforms and integrations/06-UseClaudeCodeinVSCode.md), [JetBrains](../Platforms and integrations/02-JetBrainsIDEs.md), [Desktop](../14-UseClaudeCodeDesktop.md), and [Web](../08-ClaudeCodeontheweb.md) environments above, Claude Code integrates with CI/CD, chat, and browser workflows:

| I want to...                                                                    | Best option                                                                                                         |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Continue a local session from my phone or another device                        | [Remote Control](../Platforms and integrations/04-ContinuelocalsessionsfromanydevicewithRemoteControl.md)                                                                                |
| Push events from Telegram, Discord, iMessage, or my own webhooks into a session | [Channels](../05-Pusheventsintoarunningsessionwithchannels.md)                                                                                            |
| Start a task locally, continue on mobile                                        | [Web](../08-ClaudeCodeontheweb.md) or [Claude iOS app](https://apps.apple.com/app/claude-by-anthropic/id6473753684)  |
| Run Claude on a recurring schedule                                              | [Cloud scheduled tasks](../54-Scheduletasksontheweb.md) or [Desktop scheduled tasks](../14-UseClaudeCodeDesktop.md#schedule-recurring-tasks) |
| Automate PR reviews and issue triage                                            | [GitHub Actions](../20-ClaudeCodeGitHubActions.md) or [GitLab CI/CD](../21-ClaudeCodeGitLabCICD.md)                                            |
| Get automatic code review on every PR                                           | [GitHub Code Review](../10-CodeReview.md)                                                                               |
| Route bug reports from Slack to pull requests                                   | [Slack](../Platforms and integrations/05-ClaudeCodeinSlack.md)                                                                                                  |
| Debug live web applications                                                     | [Chrome](../Platforms and integrations/01-UseClaudeCodewithChrome(beta).md)                                                                                                |
| Build custom agents for your own workflows                                      | [Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)                                                 |

## Next steps

Once you've installed Claude Code, these guides help you go deeper.

* [Quickstart](03-Quickstart.md): walk through your first real task, from exploring a codebase to committing a fix
* [Store instructions and memories](../Use Claude Code/03-HowClauderemembersyourproject.md): give Claude persistent instructions with CLAUDE.md files and auto memory
* [Common workflows](../Use Claude Code/02-Commonworkflows.md) and [best practices](../Use Claude Code/01-BestPracticesforClaudeCode.md): patterns for getting the most out of Claude Code
* [Settings](../44-ClaudeCodesettings.md): customize Claude Code for your workflow
* [Troubleshooting](../52-Troubleshooting.md): solutions for common issues
* [code.claude.com](02-ClaudeCodeoverview.md): demos, pricing, and product details
