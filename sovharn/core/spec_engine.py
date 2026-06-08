"""
规范引擎 — 定义和检查 Agent 产出标准
"""
import yaml
from pathlib import Path
from typing import Optional


class SpecEngine:
    def __init__(self, specs_dir: Path):
        self.specs_dir = specs_dir
        self.specs_dir.mkdir(parents=True, exist_ok=True)
        self._cache = {}

    def _load(self, name: str) -> Optional[dict]:
        if name in self._cache:
            return self._cache[name]
        path = self.specs_dir / f"{name}.yaml"
        if not path.exists():
            path = self.specs_dir / f"{name}.yml"
        if not path.exists():
            return None
        with open(path) as f:
            spec = yaml.safe_load(f)
        self._cache[name] = spec
        return spec

    def list_specs(self) -> list:
        specs = []
        for path in sorted(self.specs_dir.glob("*.yaml")) + sorted(self.specs_dir.glob("*.yml")):
            with open(path) as f:
                data = yaml.safe_load(f)
            if data:
                specs.append({
                    "name": data.get("name", path.stem),
                    "description": data.get("description", ""),
                    "path": path.name,
                })
        return specs

    def create_spec(self, name: str, data: dict) -> dict:
        path = self.specs_dir / f"{name}.yaml"
        with open(path, "w") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        self._cache.pop(name, None)
        return {"name": name, "status": "created"}

    def validate(self, spec_name: str, output: dict) -> list:
        """Validate output against a spec. Returns list of issues."""
        spec = self._load(spec_name)
        if not spec:
            return [f"Spec '{spec_name}' not found"]

        issues = []
        gates = spec.get("gates", [])

        for gate in gates:
            # Check minimum length
            min_len = gate.get("min_length", 0)
            if min_len:
                text = output.get("text", "") or output.get("content", "") or str(output)
                if len(text) < min_len:
                    issues.append(f"内容长度不足: {len(text)}/{min_len}")

            # Check required sections
            required_sections = gate.get("required_sections", [])
            if required_sections:
                for section in required_sections:
                    text = output.get("text", "") or output.get("content", "") or str(output)
                    if section.lower() not in text.lower():
                        issues.append(f"缺少必需章节: {section}")

        return issues
