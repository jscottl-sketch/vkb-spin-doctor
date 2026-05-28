"""
system_monitor.py — OCB-C Phase 4
Real-time CPU / RAM / GPU / Disk / Network / AI-process monitor.
Standalone: python system_monitor.py
"""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

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
            return {"ok": False, "error": "psutil not installed"}
        per_core = psutil.cpu_percent(interval=0.1, percpu=True)
        freq     = psutil.cpu_freq()
        top5     = sorted(
            [{"pid": p.info["pid"], "name": p.info["name"], "cpu": p.info["cpu_percent"]}
             for p in psutil.process_iter(["pid", "name", "cpu_percent"])
             if p.info["cpu_percent"] and p.info["cpu_percent"] > 0],
            key=lambda x: x["cpu"], reverse=True
        )[:5]
        return {
            "ok":           True,
            "overall_pct":  round(sum(per_core) / len(per_core), 1) if per_core else 0.0,
            "per_core_pct": [round(c, 1) for c in per_core],
            "freq_mhz":     round(freq.current, 0) if freq else 0,
            "top_processes": top5,
        }

    def get_ram(self) -> dict:
        if not _PSUTIL:
            return {"ok": False, "error": "psutil not installed"}
        vm = psutil.virtual_memory()
        top5 = sorted(
            [{"pid": p.info["pid"], "name": p.info["name"],
              "ram_mb": round(p.info["memory_info"].rss / 1024**2, 1) if p.info["memory_info"] else 0}
             for p in psutil.process_iter(["pid", "name", "memory_info"])
             if p.info["memory_info"]],
            key=lambda x: x["ram_mb"], reverse=True
        )[:5]
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

    def get_full_snapshot(self) -> dict:
        cpu = self.get_cpu()
        ram = self.get_ram()
        gpu = self.get_gpu()
        ai  = self.get_ai_allocation()
        disk = self.get_disk_io_instant()
        thermal = self.predict_thermal()

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
        }


if __name__ == "__main__":
    sm = SystemMonitor()
    print(json.dumps(sm.get_full_snapshot(), indent=2))
