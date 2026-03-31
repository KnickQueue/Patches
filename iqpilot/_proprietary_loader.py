#!/usr/bin/env python3
"""
Copyright © IQ.Lvbs, apart of Project Teal Lvbs, All Rights Reserved, licensed under https://konn3kt.com/tos
"""
import importlib
import os
import sys
from pathlib import Path
from types import ModuleType


class ProprietaryModuleMissing(ImportError):
  pass


def _iter_proprietary_python_roots() -> list[Path]:
  roots: list[Path] = []

  env_root_raw = os.environ.get("IQPILOT_PROPRIETARY_ROOT", "").strip()
  if env_root_raw:
    roots.append(Path(env_root_raw))

  repo_root = Path(__file__).resolve().parents[1]
  # Primary runtime install path on device.
  roots.append(repo_root / ".iqpilot")
  # Dev/build artifact bundle roots.
  roots.append(repo_root / "artifacts" / "iqpilot_model_selector_private")
  roots.append(repo_root / "artifacts" / "iqpilot_navd_private")
  roots.append(repo_root / "artifacts" / "iqpilot_hephaestusd_private")

  return [root / "python" for root in roots]


def _candidate_module_paths(python_root: Path, private_module_name: str) -> list[Path]:
  rel_parts = private_module_name.split(".")
  module_base = python_root.joinpath(*rel_parts)
  paths = [
    module_base.with_suffix(".py"),
    module_base.with_suffix(".pyc"),
  ]
  paths.extend(module_base.parent.glob(f"{module_base.name}.*.so"))
  paths.append(module_base / "__init__.py")
  paths.append(module_base / "__init__.pyc")
  paths.extend(module_base.glob("__init__.*.so"))
  return paths


def _module_root_for_name(private_module_name: str) -> Path | None:
  for python_root in _iter_proprietary_python_roots():
    if not (python_root / "iqpilot_private").exists():
      continue
    if any(path.exists() for path in _candidate_module_paths(python_root, private_module_name)):
      return python_root
  return None


def _ensure_private_path(private_module_name: str) -> None:
  resolved_root = _module_root_for_name(private_module_name)
  if resolved_root is not None:
    resolved_root_str = str(resolved_root)
    if resolved_root_str not in sys.path:
      sys.path.insert(0, resolved_root_str)
    return

  for python_root in _iter_proprietary_python_roots():
    if (python_root / "iqpilot_private").exists():
      python_root_str = str(python_root)
      if python_root_str not in sys.path:
        sys.path.insert(0, python_root_str)
      return


def _is_private_module_missing(error: ModuleNotFoundError, private_module_name: str) -> bool:
  missing = error.name or ""
  root = private_module_name.split(".", 1)[0]
  return missing == private_module_name or missing == root or missing.startswith(f"{private_module_name}.")


def _publish_module_symbols(public_module: ModuleType, private_module: ModuleType) -> None:
  skip = {
    "__name__",
    "__package__",
    "__loader__",
    "__spec__",
    "__file__",
    "__cached__",
    "__builtins__",
  }

  for key, value in private_module.__dict__.items():
    if key in skip:
      continue
    public_module.__dict__[key] = value

  public_module.__dict__["__private_module__"] = private_module.__name__
  if "__all__" not in public_module.__dict__:
    public_module.__dict__["__all__"] = [k for k in private_module.__dict__ if not k.startswith("_")]


def load_private_module(public_module_name: str, private_module_name: str) -> ModuleType:
  public_module = sys.modules[public_module_name]
  _ensure_private_path(private_module_name)

  try:
    private_module = importlib.import_module(private_module_name)
  except ModuleNotFoundError as error:
    if _is_private_module_missing(error, private_module_name):
      raise ProprietaryModuleMissing(
        f"missing proprietary module '{private_module_name}'. "
        "install the IQ Pilot private proprietary bundle into IQPILOT_PROPRIETARY_ROOT"
      ) from error
    raise

  _publish_module_symbols(public_module, private_module)
  return private_module
