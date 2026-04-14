from fastapi import APIRouter

from app.schemas.provider import ProviderSummaryResponse
from app.services.providers import ProviderFactory

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("", response_model=ProviderSummaryResponse)
def get_provider_summary() -> ProviderSummaryResponse:
    return ProviderSummaryResponse(**ProviderFactory.summary())
