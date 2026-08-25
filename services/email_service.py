from datetime import datetime, timezone
import logging
from schemas.email import EmailData, EmailGenerateRequest, EmailGenerateResponse
from utils import getLLMResponse

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def generate_email(request: EmailGenerateRequest) -> EmailGenerateResponse:
        """
        Executes email generation workflow by calling the existing getLLMResponse logic in utils.py.
        Preserves model, prompt template, and Cohere integration behavior without modification.
        """
        try:
            email_text = getLLMResponse(
                form_input=request.topic,
                email_sender=request.sender,
                email_recipient=request.recipient,
                email_style=request.style,
            )

            generated_at = datetime.now(timezone.utc).isoformat()

            data = EmailData(
                email_text=email_text,
                topic=request.topic,
                sender=request.sender,
                recipient=request.recipient,
                style=request.style,
                generated_at=generated_at,
            )

            return EmailGenerateResponse(
                success=True,
                message="Email generated successfully",
                data=data,
                error=None,
            )
        except Exception as e:
            logger.error(f"Error generating email: {str(e)}", exc_info=True)
            raise e
