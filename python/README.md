# Ready for check-in: https://github.com/vdasari03/AI

This folder contains a media-driven stock alert prototype prepared for check-in to the repository at https://github.com/vdasari03/AI.

Included code files (keep these for check-in):

- `main.py`
- `repo.py`
- `llm_mock.py`
- `llm_adapter.py`
- `processor.py`
- `alert_engine.py`
- `execution_engine.py`
- `shell_integration.py`
- `cli_detect.py`
- `shell_hook.ps1` (PowerShell helper)
- `tests/` (basic end-to-end tests)

Purpose: a minimal, deterministic prototype demonstrating media text -> LLM mock -> signals -> recommendations -> simulated execution. Replace the mock adapters with real services when integrating into the main repo.


Run:

```powershell
py main.py
```

Output: JSON with recommendations and simulated executions printed to stdout.

Files:

- `main.py`: runner that feeds sample news items through the pipeline and simulates executions.
- `repo.py`: in-memory sample stock repository.
- `llm_mock.py`: deterministic text analyzer that mimics LLM outputs.
- `llm_adapter.py`: adapter that chooses between the mock and an optional real LLM provider.
- `processor.py`: aggregates LLM signals (adds confidence, timestamps).
- `alert_engine.py`: generates BUY/SELL/HOLD recommendations and can simulate executions.
- `execution_engine.py`: deterministic simulated execution and ledger.

LLM integration:

By default the system uses the mock LLM. To use OpenAI's API, set environment variables and install the `openai` package:

```powershell
pip install openai
$env:OPENAI_API_KEY = "sk-..."
$env:LLM_MODE = "openai"
py main.py
```

Note: the `openai` integration is a minimal example and may need prompt engineering and parsing in production.

Shell / VS Code terminal integration
-------------------------------------------------
To improve command detection from your shell (PowerShell) you can enable shell integration and use the included PowerShell hook.

1) In VS Code: enable shell integration (see Terminal → Shell Integration in the UI) or search "Shell Integration" in Extensions and enable it. Also add to workspace settings (optional):

```json
{
	"terminal.integrated.shellIntegration.enabled": true
}
```

2) Load the repo PowerShell hook in your terminal session from the project root:

```powershell
.\shell_hook.ps1
# or to make it permanent, add the following line to your PowerShell profile (~\Documents\PowerShell\Microsoft.PowerShell_profile.ps1):
# . 'C:\path\to\media_driven\shell_hook.ps1'
```

3) Use the `track` helper to detect (and optionally run) trading commands:

```powershell
# detect only
track "Buy 100 AAPL at 150"

# detect and run
track "ping 127.0.0.1" -Run
```

The `track` helper calls the project's `cli_detect.py` which uses `shell_integration.detect_commands` to find explicit buy/sell commands in arbitrary text. You can adapt `shell_hook.ps1` to auto-invoke for each entered command, but that's invasive; the `track` wrapper is a safer starting point.
