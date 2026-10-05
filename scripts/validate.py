#!/usr/bin/env python3
"""Validate Game Lab environment files and portability rules."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENTS = ROOT / "deploy" / "environments"
DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)
APPROVED_DOMAIN_FILES = {
    Path("deploy/environments/production.yaml"),
}
REQUIRED_MODULES = {"web", "api", "mcp", "observability"}


def load_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: cannot load YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: top level must be a mapping")
    return data


def hostname(module: dict, base_domain: str) -> str:
    override = str(module.get("hostname", "")).strip().lower()
    if override:
        return override
    return f"{module.get('subdomain', '')}.{base_domain}".lower()


def validate_environment(path: Path) -> tuple[list[str], dict[str, str]]:
    errors: list[str] = []
    endpoints: dict[str, str] = {}
    rel = path.relative_to(ROOT)
    try:
        data = load_yaml(path)
    except ValueError as exc:
        return [str(exc)], endpoints

    platform = data.get("platform")
    modules = data.get("modules")
    ingress = data.get("ingress")
    if not isinstance(platform, dict):
        return [f"{rel}: platform must be a mapping"], endpoints
    if not isinstance(modules, dict):
        return [f"{rel}: modules must be a mapping"], endpoints
    if not isinstance(ingress, dict):
        errors.append(f"{rel}: ingress must be a mapping")

    for key in ("name", "environment", "baseDomain"):
        if not isinstance(platform.get(key), str) or not platform[key].strip():
            errors.append(f"{rel}: platform.{key} must be a non-empty string")

    base_domain = str(platform.get("baseDomain", "")).strip().lower()
    if base_domain and not DOMAIN_RE.fullmatch(base_domain):
        errors.append(f"{rel}: invalid platform.baseDomain: {base_domain!r}")

    missing = REQUIRED_MODULES - set(modules)
    if missing:
        errors.append(f"{rel}: missing modules: {', '.join(sorted(missing))}")

    seen_hosts: set[str] = set()
    for name, module in modules.items():
        if not isinstance(module, dict):
            errors.append(f"{rel}: modules.{name} must be a mapping")
            continue
        if not isinstance(module.get("enabled"), bool):
            errors.append(f"{rel}: modules.{name}.enabled must be true or false")
        if not module.get("hostname") and not module.get("subdomain"):
            errors.append(f"{rel}: modules.{name} needs subdomain or hostname")
            continue
        host = hostname(module, base_domain)
        if not DOMAIN_RE.fullmatch(host):
            errors.append(f"{rel}: modules.{name} resolves to invalid hostname {host!r}")
        if module.get("enabled"):
            if host in seen_hosts:
                errors.append(f"{rel}: duplicate enabled hostname {host!r}")
            seen_hosts.add(host)
            endpoints[name] = f"https://{host}"

    return errors, endpoints


def validate_portability() -> list[str]:
    errors: list[str] = []
    production = load_yaml(ROOT / "deploy/environments/production.yaml")
    deployment_domain = str(production["platform"]["baseDomain"]).lower()
    text_extensions = {".md", ".yaml", ".yml", ".json", ".py", ".tpl", ".txt"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix not in text_extensions:
            continue
        rel = path.relative_to(ROOT)
        if rel in APPROVED_DOMAIN_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if deployment_domain in text.lower():
            errors.append(
                f"{rel}: deployment domain must only appear in approved environment config"
            )
        if re.search(
            r"(?im)^\s*(password|token|secret|api[_-]?key)\s*:\s*(?![\"']?\$|false\s*$|true\s*$|[\"']?\s*$)[^\n]+",
            text,
        ):
            errors.append(f"{rel}: possible committed secret; inject it at deploy time")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", type=Path)
    parser.add_argument("--print-endpoints", action="store_true")
    args = parser.parse_args()

    paths = [args.environment] if args.environment else sorted(ENVIRONMENTS.glob("*.yaml"))
    errors = validate_portability()
    endpoint_sets: list[tuple[Path, dict[str, str]]] = []
    for raw_path in paths:
        path = raw_path if raw_path.is_absolute() else ROOT / raw_path
        if not path.is_file():
            errors.append(f"{raw_path}: environment file not found")
            continue
        path_errors, endpoints = validate_environment(path)
        errors.extend(path_errors)
        endpoint_sets.append((path, endpoints))

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(paths)} environment file(s); portability checks passed.")
    if args.print_endpoints:
        for path, endpoints in endpoint_sets:
            print(f"{path.relative_to(ROOT)}:")
            for name, url in sorted(endpoints.items()):
                print(f"  {name}: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
