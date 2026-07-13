
from pydantic import BaseModel, HttpUrl, field_validator

class IngestRequest(BaseModel):
    repo_url: HttpUrl

    @field_validator("repo_url")
    @classmethod
    def validate_github_url(cls, value: HttpUrl):
        url = str(value)

        if not url.startswith("https://github.com/"):
            raise ValueError("Only GitHub repository URLs are supported.")

        return value

class IngestResponse(BaseModel):
    status: str
    repository: str
    message: str