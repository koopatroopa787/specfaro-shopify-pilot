"""Run untrusted repair commands in a credential-free Docker container.

Only a copied project directory is mounted. The controller keeps the model key,
official-doc tool, patch policy, and Docker socket outside the container.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid

from openhands.sdk.tool import ToolExecutor, register_tool
from openhands.tools.file_editor.definition import FileEditorAction, FileEditorObservation, FileEditorTool
from openhands.tools.file_editor.impl import FileEditorExecutor
from openhands.tools.terminal.definition import TerminalAction, TerminalObservation, TerminalTool
from openhands.tools.terminal.metadata import CmdOutputMetadata


DEFAULT_IMAGE = "node:22-bookworm-slim"
MAX_TERMINAL_SECONDS = 120
MAX_OUTPUT_CHARS = 8_000


class SandboxUnavailable(RuntimeError):
    """The required container boundary could not be established."""


class DockerCommandRunner:
    def __init__(self, image: str = DEFAULT_IMAGE):
        if os.name != "posix" or not hasattr(os, "getuid"):
            raise SandboxUnavailable("Docker repair isolation requires a Linux runner")
        self.docker = shutil.which("docker")
        if not self.docker:
            raise SandboxUnavailable("Docker CLI is unavailable")
        if not image or any(char.isspace() for char in image):
            raise SandboxUnavailable("Invalid sandbox image")
        self.image = image

    def _invoke(self, workspace: Path, command: list[str], timeout: int) -> dict:
        root = workspace.resolve(strict=True)
        if not root.is_dir() or workspace.is_symlink():
            raise SandboxUnavailable("Sandbox workspace must be a real directory")
        # The caller's environment contains SPECFARO_DEEPSEEK_API_KEY. Never
        # inherit it into either the Docker CLI process or the container.
        client_env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                      "HOME": "/tmp", "DOCKER_CONFIG": "/tmp/specfaro-docker-config"}
        container_name = "specfaro-" + uuid.uuid4().hex[:20]
        argv = [self.docker, "run", "--rm", "--name", container_name,
                "--network=none", "--read-only",
                "--cap-drop=ALL", "--security-opt=no-new-privileges",
                "--pids-limit=128", "--memory=768m", "--cpus=1",
                "--user", f"{os.getuid()}:{os.getgid()}",
                "--workdir", "/workspace",
                "--tmpfs", "/tmp:rw,nosuid,nodev,size=128m",
                "--mount", f"type=bind,source={root},target=/workspace",
                "--env", "HOME=/tmp", "--env", "CI=true",
                "--env", "npm_config_cache=/tmp/npm-cache",
                "--env", "PATH=/usr/local/bin:/usr/bin:/bin",
                self.image, *command]
        started = time.monotonic()
        try:
            result = subprocess.run(argv, cwd=root, env=client_env,
                                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True, errors="replace",
                                    timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            subprocess.run([self.docker, "rm", "-f", container_name], env=client_env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=10, check=False)
            return {"status": "failed", "reason": f"Timed out after {timeout} seconds",
                    "seconds": round(time.monotonic() - started, 2),
                    "stdout": str(exc.stdout or "")[-MAX_OUTPUT_CHARS:],
                    "stderr": str(exc.stderr or "")[-MAX_OUTPUT_CHARS:]}
        except OSError as exc:
            return {"status": "failed", "reason": str(exc)[:500],
                    "seconds": round(time.monotonic() - started, 2),
                    "stdout": "", "stderr": ""}
        return {"status": "passed" if result.returncode == 0 else "failed",
                "exit_code": result.returncode,
                "seconds": round(time.monotonic() - started, 2),
                "stdout": result.stdout[-MAX_OUTPUT_CHARS:],
                "stderr": result.stderr[-MAX_OUTPUT_CHARS:]}

    def run_argv(self, argv: list[str], workspace: Path, timeout: int) -> dict:
        if not argv or len(argv) > 24 or any(not isinstance(x, str) or not x for x in argv):
            raise ValueError("Invalid validation command")
        return self._invoke(workspace, argv, timeout)

    def run_shell(self, command: str, workspace: Path, timeout: int) -> dict:
        if not command or len(command) > 16_000:
            raise ValueError("Invalid sandbox shell command")
        return self._invoke(workspace, ["/bin/sh", "-lc", command], timeout)


class SandboxTerminalExecutor(ToolExecutor):
    def __init__(self, root: Path, runner: DockerCommandRunner):
        self.root = root
        self.runner = runner

    def __call__(self, action: TerminalAction, conversation=None) -> TerminalObservation:
        if action.is_input or action.reset or not action.command:
            return TerminalObservation.from_text(
                text="This sandbox runs one complete command per call; interactive input is unavailable.",
                command=action.command, exit_code=2, is_error=True)
        timeout = min(MAX_TERMINAL_SECONDS, max(1, int(action.timeout or 30)))
        result = self.runner.run_shell(action.command, self.root, timeout)
        output = (result.get("stdout", "") + result.get("stderr", ""))[-MAX_OUTPUT_CHARS:]
        return TerminalObservation.from_text(
            text=output, command=action.command,
            exit_code=result.get("exit_code", 124),
            timeout="Timed out" in result.get("reason", ""),
            is_error=result["status"] != "passed",
            metadata=CmdOutputMetadata(exit_code=result.get("exit_code", 124),
                                       working_dir="/workspace"))


class SandboxedTerminalTool(TerminalTool):
    name = "sandboxed_terminal"

    @classmethod
    def create(cls, conv_state, *, image: str = DEFAULT_IMAGE):
        root = Path(conv_state.workspace.working_dir)
        return [cls(action_type=TerminalAction, observation_type=TerminalObservation,
                    description=("Run one non-interactive shell command in a network-disabled "
                                 "container. The project is at /workspace. Each call starts "
                                 "in /workspace; shell state does not persist. No secrets or "
                                 "host files are available."),
                    executor=SandboxTerminalExecutor(root, DockerCommandRunner(image)))]


class GuardedFileEditorExecutor(FileEditorExecutor):
    def __init__(self, root: Path, focus: list[str]):
        self.root = root.resolve(strict=True)
        allowed = [str((self.root / name).resolve()) for name in focus]
        super().__init__(workspace_root=str(self.root), allowed_edits_files=allowed)

    def __call__(self, action: FileEditorAction, conversation=None) -> FileEditorObservation:
        target = Path(action.path)
        if action.path == "/workspace":
            target = self.root
        elif action.path.startswith("/workspace/"):
            target = self.root / action.path.removeprefix("/workspace/")
        if not target.is_absolute():
            target = self.root / target
        resolved = target.resolve()
        if not resolved.is_relative_to(self.root):
            return FileEditorObservation.from_text(
                text="File path is outside the isolated project copy",
                command=action.command, is_error=True)
        return super().__call__(action.model_copy(update={"path": str(resolved)}), conversation)


class SandboxedFileEditorTool(FileEditorTool):
    name = "sandboxed_file_editor"

    @classmethod
    def create(cls, conv_state, *, focus: list[str]):
        root = Path(conv_state.workspace.working_dir)
        return [cls(action_type=FileEditorAction, observation_type=FileEditorObservation,
                    description=("View files inside the project copy and edit only these "
                                 f"production files: {', '.join(focus)}. "
                                 "Use project-relative paths or paths under the workspace."),
                    executor=GuardedFileEditorExecutor(root, focus))]


register_tool(SandboxedTerminalTool.name, SandboxedTerminalTool)
register_tool(SandboxedFileEditorTool.name, SandboxedFileEditorTool)
