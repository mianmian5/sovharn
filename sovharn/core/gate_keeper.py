"""
安全关闸 — 工具权限、内容过滤、成本控制
"""
import yaml, time
from pathlib import Path
from typing import Optional


class GateKeeper:
    def __init__(self, gates_dir: Path):
        self.gates_dir = gates_dir
        self.gates_dir.mkdir(parents=True, exist_ok=True)

    def check_tool_call(self, tool_name: str, agent_name: str, args: dict = None) -> dict:
        """Check if a tool call is allowed. Returns {allowed: bool, reason: str}"""
        for gate_file in self.gates_dir.glob("*.yaml"):
            with open(gate_file) as f:
                try:
                    gate = yaml.safe_load(f)
                except:
                    continue
            if not gate:
                continue
            rules = gate.get("rules", [])
            for rule in rules:
                if self._match_rule(rule, tool_name, agent_name, args):
                    action = rule.get("action", "allow")
                    if action == "deny":
                        return {"allowed": False, "reason": rule.get("reason", "工具调用被拒绝")}
                    elif action == "review":
                        return {"allowed": True, "review": True, "reason": rule.get("reason", "需要人工确认")}
        return {"allowed": True}

    def _match_rule(self, rule: dict, tool: str, agent: str, args: dict = None) -> bool:
        tool_pattern = rule.get("tool", "")
        agent_pattern = rule.get("agent", "")
        if tool_pattern and tool_pattern not in tool:
            return False
        if agent_pattern and agent_pattern not in agent:
            return False
        return True

    def check_content(self, content: str) -> dict:
        """Basic content safety filter"""
        dangerous_patterns = [
            "rm -rf /", "format ", "DROP TABLE", "DELETE FROM",
        ]
        for pattern in dangerous_patterns:
            if pattern.lower() in content.lower():
                return {"safe": False, "reason": f"检测到危险模式: {pattern}"}
        return {"safe": True}
