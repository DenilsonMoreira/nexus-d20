from fastapi import APIRouter

from app.domain.rules.attack import resolve_attack
from app.domain.rules.durability import durability_snapshot
from app.domain.rules.encumbrance import calculate_encumbrance
from app.domain.rules.rest import simulate_long_rest
from app.schemas.rules import (
    AttackRequest,
    AttackResponse,
    DurabilityPreviewRequest,
    DurabilitySnapshotResponse,
    EncumbranceRequest,
    EncumbranceResponse,
    LongRestRequest,
    LongRestResponse,
)

router = APIRouter()


@router.post("/attacks/resolve", response_model=AttackResponse)
def attack(payload: AttackRequest) -> AttackResponse:
    return AttackResponse.model_validate(resolve_attack(payload.model_dump()))


@router.post("/durability/preview", response_model=DurabilitySnapshotResponse)
def durability(payload: DurabilityPreviewRequest) -> DurabilitySnapshotResponse:
    return DurabilitySnapshotResponse.model_validate(durability_snapshot(**payload.model_dump()))


@router.post("/encumbrance/calculate", response_model=EncumbranceResponse)
def encumbrance(payload: EncumbranceRequest) -> EncumbranceResponse:
    return EncumbranceResponse.model_validate(calculate_encumbrance(**payload.model_dump()))


@router.post("/long-rest/simulate", response_model=LongRestResponse)
def long_rest(payload: LongRestRequest) -> LongRestResponse:
    return LongRestResponse.model_validate(simulate_long_rest(payload.model_dump()))
