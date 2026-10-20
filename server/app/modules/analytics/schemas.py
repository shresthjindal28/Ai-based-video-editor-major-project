from pydantic import BaseModel


class UsageSummary(BaseModel):
    projects: int
    assets: int
    jobs: int
    renders: int
    storage_bytes: int
