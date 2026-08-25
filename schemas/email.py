from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


class EmailGenerateRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        description="Topic or content details for the email",
        examples=["Leave request for 2 days due to personal work"],
    )
    sender: str = Field(
        ...,
        min_length=1,
        description="Name of the email sender",
        examples=["Mohit"],
    )
    recipient: str = Field(
        ...,
        min_length=1,
        description="Name of the email recipient",
        examples=["Manager"],
    )
    style: str = Field(
        default="Formal",
        description="Writing style for the email (e.g., Formal, Appreciating, Not Satisfied, Neutral)",
        examples=["Formal"],
    )

    @field_validator("topic", "sender", "recipient", "style", mode="before")
    @classmethod
    def validate_non_empty_strings(cls, v: Any, info) -> Any:
        if isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped and info.field_name in ("topic", "sender", "recipient"):
                raise ValueError(f"Field '{info.field_name}' must not be empty or whitespace only.")
            return v_stripped if v_stripped else v
        return v


class EmailData(BaseModel):
    email_text: str = Field(..., description="Generated email body text")
    topic: str = Field(..., description="Topic of the email")
    sender: str = Field(..., description="Sender name")
    recipient: str = Field(..., description="Recipient name")
    style: str = Field(..., description="Writing style used")
    generated_at: str = Field(..., description="ISO timestamp of email generation")


class EmailGenerateResponse(BaseModel):
    success: bool = Field(True, description="Indicates if request was successful")
    message: str = Field("Email generated successfully", description="Status message")
    data: Optional[EmailData] = Field(None, description="Generated email payload")
    error: Optional[Any] = Field(None, description="Error detail if any")


class APIErrorDetails(BaseModel):
    code: str = Field(..., description="Error code string")
    detail: Any = Field(..., description="Detailed description of the error")


class APIErrorResponse(BaseModel):
    success: bool = Field(False, description="Indicates request failed")
    message: str = Field(..., description="Failure summary message")
    data: Optional[Any] = Field(None, description="Always null for error responses")
    error: APIErrorDetails = Field(..., description="Structured error payload")
