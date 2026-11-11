"""Formato do projeto e gravação atômica: nada é executado ao abrir JSON."""
import json
import os
import tempfile
from pathlib import Path
from copy import deepcopy
from .geometry import validate_geometry


def new_project():
    return {"format": "motorlab-project", "version": 2,
            "name": "Novo projeto", "description": "", "files": [],
            "geometry": {"units": "mm", "shapes": []}}


def validate_project(data):
    if not isinstance(data, dict) or data.get("format") != "motorlab-project":
        raise ValueError("Este arquivo não é um projeto MotorLab.")
    data = deepcopy(data)
    version = data.get("version")
    if type(version) is not int or version not in (1, 2):
        raise ValueError("Versão de projeto não suportada.")
    if version == 1:
        if set(data) != {"format", "version", "name", "description", "files"}:
            raise ValueError("Estrutura de projeto incompatível.")
        data["version"] = 2
        data["geometry"] = {"units": "mm", "shapes": []}
    if set(data) != set(new_project()):
        raise ValueError("Estrutura de projeto incompatível.")
    if not all(isinstance(data[k], str) for k in ("name", "description")):
        raise ValueError("Nome e descrição devem ser textos.")
    if not isinstance(data["files"], list) or not all(isinstance(p, str) for p in data["files"]):
        raise ValueError("A lista de arquivos é inválida.")
    data["geometry"] = validate_geometry(data["geometry"])
    return data


def load_project(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return validate_project(json.load(stream))


def save_project(path, data):
    data = validate_project(data)
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".motorlab-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
