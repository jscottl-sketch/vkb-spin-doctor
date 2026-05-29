"""
system_monitor.py — OCB-C Phase 4
Real-time CPU / RAM / GPU / Disk / Network / AI-process monitor.
Standalone: python system_monitor.py
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent

# HC-06: baseline RSS at session start (set on first call)
_session_start_rss_mb: float = 0.0

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

try:
    import GPUtil
    _GPUTIL = True
except ImportError:
    _GPUTIL = False

# AI-related process name fragments to detect
_AI_PROCS = {"lm studio", "python", "node", "mcc_server", "loop_manager", "aafl"}

# Track last 10 GPU temps for thermal prediction
_gpu_temp_history: list[float] = []

# Non-blocking disk IO cache (avoids sleep in each call)
_last_disk_counters = None
_last_disk_time: float = 0.0


class SystemMonitor:

    def get_cpu(self) -> dict:
        if not _PSUTIL:
            return {"ok": True, "overall_pct": 0.0, "per_core_pct": [], "freq_mhz": 0, "top_processes": []}
        try:
            per_core = psutil.cpu_percent(interval=0.1, percpu=True)
        except Exception:
            per_core = []
        try:
            freq = psutil.cpu_freq()
        except Exception:
            freq = None
        try:
            top5 = sorted(
                [{"pid": p.info["pid"], "name": p.info["name"], "cpu": p.info["cpu_percent"]}
                 for p in psutil.process_iter(["pid", "name", "cpu_percent"])
                 if p.info["cpu_percent"] and p.info["cpu_percent"] > 0],
                key=lambda x: x["cpu"], reverse=True
            )[:5]
        except Exception:
            top5 = []
        return {
            "ok":           True,
            "overall_pct":  round(sum(per_core) / len(per_core), 1) if per_core else 0.0,
            "per_core_pct": [round(c, 1) for c in per_core],
            "freq_mhz":     round(freq.current, 0) if freq else 0,
            "top_processes": top5,
        }

    def get_ram(self) -> dict:
        if not _PSUTIL:
            return {"ok": True, "total_gb": 0.0, "used_gb": 0.0, "free_gb": 0.0, "percent": 0.0, "top_processes": []}
        try:
            vm = psutil.virtual_memory()
        except Exception:
            return {"ok": True, "total_gb": 0.0, "used_gb": 0.0, "free_gb": 0.0, "percent": 0.0, "top_processes": []}
        try:
            top5 = sorted(
                [{"pid": p.info["pid"], "name": p.info["name"],
                  "ram_mb": round(p.info["memory_info"].rss / 1024**2, 1) if p.info["memory_info"] else 0}
                 for p in psutil.process_iter(["pid", "name", "memory_info"])
                 if p.info["memory_info"]],
                key=lambda x: x["ram_mb"], reverse=True
            )[:5]
        except Exception:
            top5 = []
        return {
            "ok":          True,
            "total_gb":    round(vm.total / 1024**3, 2),
            "used_gb":     round(vm.used / 1024**3, 2),
            "free_gb":     round(vm.available / 1024**3, 2),
            "percent":     vm.percent,
            "top_processes": top5,
        }

    def get_gpu(self) -> dict:
        result = {"ok": True, "gpus": [], "top_processes": []}

        if _GPUTIL:
            try:
                gpus = GPUtil.getGPUs()
                for g in gpus:
                    entry = {
                        "id":          g.id,
                        "name":        g.name,
                        "load_pct":    round(g.load * 100, 1),
                        "vram_total_gb": round(g.memoryTotal / 1024, 2),
                        "vram_used_gb":  round(g.memoryUsed / 1024, 2),
                        "vram_free_gb":  round(g.memoryFree / 1024, 2),
                        "temperature_c": g.temperature,
                        "fan_speed_pct": getattr(g, "fanSpeed", None),
                    }
                    result["gpus"].append(entry)
                    # Track temp for thermal prediction
                    if g.temperature:
                        _gpu_temp_history.append(float(g.temperature))
                        if len(_gpu_temp_history) > 10:
                            _gpu_temp_history.pop(0)
            except Exception as exc:
                result["ok"] = False
                result["error"] = str(exc)

        # Try nvidia-smi for top processes
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-compute-apps=pid,name,used_memory",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5,
            )
            for line in out.stdout.strip().splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    result["top_processes"].append({
                        "pid":        parts[0],
                        "name":       parts[1],
                        "vram_mb":    parts[2],
                    })
        except Exception:
            pass

        if not result["gpus"] and not result.get("error"):
            result["error"] = "No GPU detected or GPUtil unavailable"

        return result

    def get_disk_io_instant(self) -> dict:
        """Non-blocking disk IO — uses cached counters from previous call."""
        global _last_disk_counters, _last_disk_time
        if not _PSUTIL:
            return {"ok": False, "error": "psutil not installed"}
        try:
            now = time.time()
            c = psutil.disk_io_counters()
            if _last_disk_counters is None or _last_disk_time == 0.0:
                _last_disk_counters = c
                _last_disk_time = now
                return {"ok": True, "read_mb_s": 0.0, "write_mb_s": 0.0}
            elapsed = max(now - _last_disk_time, 0.01)
            result = {
                "ok":        True,
                "read_mb_s": round((c.read_bytes  - _last_disk_counters.read_bytes)  / 1024**2 / elapsed, 2),
                "write_mb_s": round((c.write_bytes - _last_disk_counters.write_bytes) / 1024**2 / elapsed, 2),
            }
            _last_disk_counters = c
            _last_disk_time = now
            return result
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def get_disk_io(self) -> dict:
        if not _PSUTIL:
            return {"ok": False, "error": "psutil not installed"}
        try:
            c1 = psutil.disk_io_counters()
            time.sleep(0.5)
            c2 = psutil.disk_io_counters()
            return {
                "ok":             True,
                "read_mb_s":      round((c2.read_bytes - c1.read_bytes) / 1024**2 / 0.5, 2),
                "write_mb_s":     round((c2.write_bytes - c1.write_bytes) / 1024**2 / 0.5, 2),
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def get_network(self) -> dict:
        if not _PSUTIL:
            return {"ok": False, "error": "psutil not installed"}
        try:
            c1 = psutil.net_io_counters()
            time.sleep(0.5)
            c2 = psutil.net_io_counters()
            return {
                "ok":             True,
                "upload_mb_s":    round((c2.bytes_sent - c1.bytes_sent) / 1024**2 / 0.5, 3),
                "download_mb_s":  round((c2.bytes_recv - c1.bytes_recv) / 1024**2 / 0.5, 3),
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def get_ai_allocation(self) -> dict:
        if not _PSUTIL:
            return {"ok": False, "error": "psutil not installed"}
        ai_procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "cmdline"]):
            try:
                name = (p.info["name"] or "").lower()
                cmd  = " ".join(p.info["cmdline"] or []).lower()
                if any(k in name or k in cmd for k in _AI_PROCS):
                    ram_mb = round(p.info["memory_info"].rss / 1024**2, 1) if p.info["memory_info"] else 0
                    ai_procs.append({
                        "pid":    p.info["pid"],
                        "name":   p.info["name"],
                        "cpu_pct":  round(p.info["cpu_percent"] or 0, 1),
                        "ram_mb":   ram_mb,
                        "gpu_mb":   None,  # GPU per-process not available without nvidia-smi
                        "status":   "running",
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return {"ok": True, "processes": ai_procs}

    def predict_thermal(self) -> dict:
        if len(_gpu_temp_history) < 3:
            return {"ok": True, "prediction": "stable", "data_points": len(_gpu_temp_history)}
        temps = _gpu_temp_history[-6:]  # last 6 readings
        slope = (temps[-1] - temps[0]) / max(len(temps)-1, 1)
        if slope <= 0:
            return {"ok": True, "prediction": "stable", "slope_c_per_reading": round(slope, 2)}
        current_temp = temps[-1]
        throttle_temp = 85
        if current_temp >= throttle_temp:
            return {"ok": True, "prediction": "throttling_now", "current_c": current_temp}
        readings_to_throttle = (throttle_temp - current_temp) / slope
        return {
            "ok":                True,
            "prediction":        "rising",
            "current_c":         current_temp,
            "slope_c_per_reading": round(slope, 2),
            "readings_to_throttle": round(readings_to_throttle, 1),
        }

    def check_disk_space(self) -> dict:
        """HC-03: Check free space on C: and D:. Warn if either < 10GB free."""
        results = []
        status = "PASS"
        for drive in ("C:\\", "D:\\"):
            try:
                usage = shutil.disk_usage(drive)
                free_gb = round(usage.free / 1024 ** 3, 1)
                label = f"{drive} {free_gb}GB free"
                if free_gb < 10:
                    label += " (WARN: <10GB)"
                    status = "WARN"
                results.append(label)
            except Exception:
                results.append(f"{drive} unavailable")
        return {"name": "HC-03 Disk Space", "status": status,
                "detail": " | ".join(results)}

    def track_memory_rss(self) -> dict:
        """HC-06: Log current process RSS to data/memory_log.json. Warn if grown > 500MB."""
        global _session_start_rss_mb
        if not _PSUTIL:
            return {"name": "HC-06 Memory RSS", "status": "FAIL",
                    "detail": "psutil not installed"}
        try:
            import psutil as _ps
            rss_mb = round(_ps.Process(os.getpid()).memory_info().rss / 1024 ** 2, 1)
            if _session_start_rss_mb == 0.0:
                _session_start_rss_mb = rss_mb

            log_path = HERE / "data" / "memory_log.json"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            entries = []
            if log_path.exists():
                try:
                    entries = json.loads(log_path.read_text(encoding="utf-8"))
                except Exception:
                    entries = []
            entries.append({"ts": datetime.now().isoformat(timespec="seconds"), "rss_mb": rss_mb})
            if len(entries) > 100:
                entries = entries[-100:]
            log_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

            growth = round(rss_mb - _session_start_rss_mb, 1)
            detail = f"RSS: {rss_mb}MB (start: {_session_start_rss_mb}MB, growth: +{growth}MB)"
            if growth > 500:
                detail += " — WARNING: >500MB growth since session start"
                return {"name": "HC-06 Memory RSS", "status": "WARN", "detail": detail}
            return {"name": "HC-06 Memory RSS", "status": "PASS", "detail": detail}
        except Exception as exc:
            return {"name": "HC-06 Memory RSS", "status": "FAIL", "detail": f"Error: {exc}"}

    def get_full_snapshot(self) -> dict:
        cpu = self.get_cpu()
        ram = self.get_ram()
        gpu = self.get_gpu()
        ai  = self.get_ai_allocation()
        disk = self.get_disk_io_instant()
        thermal = self.predict_thermal()
        disk_space = self.check_disk_space()
        memory_rss = self.track_memory_rss()

        # Composite health score 0–100
        cpu_score = max(0, 100 - cpu.get("overall_pct", 0))
        ram_score = max(0, 100 - ram.get("percent", 0))
        gpu_load  = gpu.get("gpus", [{}])[0].get("load_pct", 0) if gpu.get("gpus") else 0
        gpu_score = max(0, 100 - gpu_load)
        health_score = round((cpu_score + ram_score + gpu_score) / 3, 1)

        # Bottleneck detection
        bottleneck = "balanced"
        if cpu.get("overall_pct", 0) > 80:
            bottleneck = "cpu-bound"
        elif ram.get("percent", 0) > 80:
            bottleneck = "ram-bound"
        elif gpu_load > 80:
            bottleneck = "gpu-bound"

        # Game vs AI conflict check
        ai_procs = ai.get("processes", [])
        ai_on_gpu = any(p.get("gpu_mb") and float(p["gpu_mb"] or 0) > 0 for p in ai_procs)
        game_names = {"warthunder", "warframe", "starcitizen", "ed", "arma", "steam"}
        game_running = any(
            any(g in (p.get("name","").lower()) for g in game_names)
            for p in ai_procs
        )
        conflict = ai_on_gpu and game_running and gpu_load > 50

        return {
            "ok":              True,
            "timestamp":       datetime.now().isoformat(timespec="seconds"),
            "cpu":             cpu,
            "ram":             ram,
            "gpu":             gpu,
            "disk":            disk,
            "ai_allocation":   ai,
            "thermal":         thermal,
            "health_score":    health_score,
            "bottleneck":      bottleneck,
            "game_ai_conflict": conflict,
            "disk_space_check": disk_space,
            "memory_rss_check": memory_rss,
        }


if __name__ == "__main__":
    sm = SystemMonitor()
    print(json.dumps(sm.get_full_snapshot(), indent=2))
