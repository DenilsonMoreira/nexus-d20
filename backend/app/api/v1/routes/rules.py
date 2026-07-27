from fastapi import APIRouter

from app.domain.rules.ability_score_progression import (
    simulate_ability_score_improvement,
)
from app.domain.rules.attack import resolve_attack
from app.domain.rules.class_progression import simulate_class_level_up
from app.domain.rules.durability import durability_snapshot
from app.domain.rules.encumbrance import calculate_encumbrance
from app.domain.rules.progression import simulate_next_level
from app.domain.rules.rest import simulate_long_rest
from app.schemas.rules import (
    AbilityScoreImprovementSimulationRequest,
    AbilityScoreImprovementSimulationResponse,
    AttackRequest,
    AttackResponse,
    ClassProgressionSimulationRequest,
    ClassProgressionSimulationResponse,
    DurabilityPreviewRequest,
    DurabilitySnapshotResponse,
    EncumbranceRequest,
    EncumbranceResponse,
    LongRestRequest,
    LongRestResponse,
    ProgressionSimulationRequest,
    ProgressionSimulationResponse,
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


@router.post(
    "/progression/simulate",
    response_model=ProgressionSimulationResponse,
)
def progression(
    payload: ProgressionSimulationRequest,
) -> ProgressionSimulationResponse:
    return ProgressionSimulationResponse.model_validate(
        simulate_next_level(**payload.model_dump())
    )


@router.post(
    "/progression/classes/simulate",
    response_model=ClassProgressionSimulationResponse,
)
def class_progression(
    payload: ClassProgressionSimulationRequest,
) -> ClassProgressionSimulationResponse:
    return ClassProgressionSimulationResponse.model_validate(
        simulate_class_level_up(**payload.model_dump())
    )


@router.post(
    "/progression/ability-scores/simulate",
    response_model=AbilityScoreImprovementSimulationResponse,
)
def ability_score_progression(
    payload: AbilityScoreImprovementSimulationRequest,
) -> AbilityScoreImprovementSimulationResponse:
    values = payload.model_dump()
    return AbilityScoreImprovementSimulationResponse.model_validate(
        simulate_ability_score_improvement(**values)
    )
