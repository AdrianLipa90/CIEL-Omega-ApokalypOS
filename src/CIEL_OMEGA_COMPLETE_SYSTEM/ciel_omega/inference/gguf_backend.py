from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, subprocess, time, urllib.request, urllib.error

@dataclass
class GGUFBackendConfig:
    llama_server_path: str
    model_path: str
    host: str = "127.0.0.1"
    port: int = 18080
    ctx_size: int = 1024
    ngl: int = 0
    no_warmup: bool = True

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

class GGUFBackendRunner:
    def __init__(self, config: GGUFBackendConfig):
        self.config = config
        self.proc: subprocess.Popen | None = None

    def is_alive(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.config.base_url}/health", timeout=2) as r:
                return r.status == 200
        except Exception:
            return False

    def start(self, log_path: str | Path) -> None:
        log_path = Path(log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_f = open(log_path, "w", encoding="utf-8")
        cmd = [
            self.config.llama_server_path,
            "-m", self.config.model_path,
            "--host", self.config.host,
            "--port", str(self.config.port),
            "-ngl", str(self.config.ngl),
            "-c", str(self.config.ctx_size),
        ]
        if self.config.no_warmup:
            cmd.append("--no-warmup")
        self.proc = subprocess.Popen(cmd, stdout=log_f, stderr=subprocess.STDOUT)

    def wait_until_ready(self, timeout_s: int = 180) -> bool:
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            if self.proc is not None and self.proc.poll() is not None:
                return False
            if self.is_alive():
                try:
                    with urllib.request.urlopen(f"{self.config.base_url}/v1/models", timeout=3) as r:
                        if r.status == 200:
                            return True
                except Exception:
                    pass
            time.sleep(1)
        return False

    def stop(self) -> None:
        if self.proc is None:
            return
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()

    def list_models(self) -> dict:
        with urllib.request.urlopen(f"{self.config.base_url}/v1/models", timeout=20) as r:
            return json.loads(r.read().decode("utf-8", "replace"))

    def chat(self, model: str, messages: list[dict], temperature: float = 0.0, max_tokens: int = 64) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        req = urllib.request.Request(
            f"{self.config.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
