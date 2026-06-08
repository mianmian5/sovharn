"""
三层记忆系统 — Session → Daily → Permanent
"""
import json, os, time, re
from pathlib import Path
from datetime import datetime


class MemoryManager:
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.session_dir = memory_dir / "session"
        self.daily_dir = memory_dir / "daily"
        self.permanent_dir = memory_dir / "permanent"
        for d in [self.session_dir, self.daily_dir, self.permanent_dir]:
            d.mkdir(parents=True, exist_ok=True)
        self._sessions = {}  # in-memory session cache

    # ─── Session 记忆 ────────────────────────────

    def get_session(self, session_id: str) -> list:
        return self._sessions.get(session_id, [])

    def append_session(self, session_id: str, role: str, content: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({
            "role": role, "content": content, "ts": time.time()
        })

    def clear_session(self, session_id: str):
        self._sessions.pop(session_id, None)

    # ─── Daily 记忆 ─────────────────────────────

    def get_daily_path(self, date_str: str = None) -> Path:
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        return self.daily_dir / f"{date_str}.md"

    def append_daily(self, agent: str, summary: str):
        path = self.get_daily_path()
        mode = "a" if path.exists() else "w"
        with open(path, "a", encoding="utf-8") as f:
            if mode == "w":
                f.write(f"# {datetime.now().strftime('%Y-%m-%d')} 日常记录\n\n")
            ts = datetime.now().strftime("%H:%M")
            f.write(f"- [{ts}] [{agent}] {summary}\n")

    def get_daily(self, date_str: str = None) -> str:
        path = self.get_daily_path(date_str)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def list_daily(self, limit: int = 30) -> list:
        files = sorted(self.daily_dir.glob("*.md"), reverse=True)
        result = []
        for f in files[:limit]:
            result.append({"date": f.stem, "preview": f.read_text(encoding="utf-8")[:200]})
        return result

    # ─── Permanent 记忆 ──────────────────────────

    def get_permanent_path(self, topic: str) -> Path:
        safe = re.sub(r"[^a-z0-9_\-\u4e00-\u9fff]", "_", topic.lower())[:50]
        return self.permanent_dir / f"{safe}.md"

    def save_permanent(self, topic: str, content: str):
        path = self.get_permanent_path(topic)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        header = f"# {topic}\n> 更新于 {ts}\n\n"
        if path.exists():
            existing = path.read_text(encoding="utf-8")
            # Append instead of overwrite
            mode = "a"
            content = f"\n---\n\n### 更新 ({ts})\n{content}\n"
        else:
            mode = "w"
            content = header + content + "\n"
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)

    def get_permanent(self, topic: str = None) -> str:
        if topic:
            path = self.get_permanent_path(topic)
            if path.exists():
                return path.read_text(encoding="utf-8")
            return ""
        # Return all permanent memory index
        files = sorted(self.permanent_dir.glob("*.md"))
        parts = []
        for f in files:
            parts.append(f"## {f.stem}\n{f.read_text(encoding='utf-8')[:300]}...")
        return "\n\n".join(parts)

    def search_permanent(self, keyword: str) -> list:
        results = []
        for f in self.permanent_dir.glob("*.md"):
            content = f.read_text(encoding="utf-8")
            if keyword.lower() in content.lower():
                results.append({"topic": f.stem, "preview": content[:300]})
        return results

    # ─── 蒸馏 ─────────────────────────────────

    async def distill(self, session_id: str) -> dict:
        """将会话记忆蒸馏到 daily 和 permanent"""
        session = self._sessions.get(session_id, [])
        if not session:
            return {"status": "empty", "session_id": session_id}

        # Extract agent names and key content
        agents_seen = set()
        summaries = []
        for msg in session:
            agents_seen.add(msg.get("role", "unknown"))
            content = msg.get("content", "")[:100]
            if content.strip():
                summaries.append(f"[{msg['role']}] {content}")

        # Save daily
        for agent in agents_seen:
            daily_summary = "; ".join(s for s in summaries if agent in s or s.startswith(f"[{agent}]"))
            if daily_summary:
                self.append_daily(agent, daily_summary[:200])

        # Clear session
        self.clear_session(session_id)

        return {
            "status": "distilled",
            "agents": list(agents_seen),
            "entries": len(summaries),
        }

    # ─── Stats ─────────────────────────────────

    def get_stats(self) -> dict:
        return {
            "session_count": len(self._sessions),
            "daily_files": len(list(self.daily_dir.glob("*.md"))),
            "permanent_files": len(list(self.permanent_dir.glob("*.md"))),
        }
