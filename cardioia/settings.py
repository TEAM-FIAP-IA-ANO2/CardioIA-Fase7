"""Configuração central obtida exclusivamente do ambiente."""
from dataclasses import dataclass
import os
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    project_root: Path
    database_path: Path
    device_api_key: str
    cors_origins: tuple[str, ...]
    default_mode: str

    @classmethod
    def from_env(cls) -> "Settings":
        root = Path(__file__).resolve().parents[1]
        origins = tuple(x.strip() for x in os.getenv("CARDIOIA_CORS_ORIGINS", "http://localhost:5173,http://localhost:8081").split(",") if x.strip())
        return cls(
            project_root=root,
            database_path=Path(os.getenv("CARDIOIA_DATABASE", str(root / ".runtime" / "cardioia.db"))),
            device_api_key=os.getenv("CARDIOIA_DEVICE_API_KEY", ""),
            cors_origins=origins,
            default_mode=os.getenv("CARDIOIA_DEFAULT_MODE", "local"),
        )
