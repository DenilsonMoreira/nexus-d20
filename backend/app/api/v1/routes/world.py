import copy
import uuid
from decimal import Decimal

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.dependencies import (
    CampaignAccessDependency,
    CampaignMaster,
    CurrentUser,
    DatabaseSession,
)
from app.core.errors import AppError
from app.domain.rules.encumbrance import calculate_encumbrance
from app.domain.rules.world import (
    fatigue_dc,
    generate_weighted_encounter,
    plan_travel,
    sanitize_public_payload,
)
from app.models import Character, ItemInstance, ItemTemplateVersion
from app.models.world import (
    Creature,
    DashboardLayout,
    Encounter,
    KnowledgeEdge,
    KnowledgeNode,
    LibraryEntry,
    Shop,
    ShopStock,
    TravelPlan,
)
from app.schemas.world import (
    CreatureCreate,
    CreatureUpdate,
    DashboardCreate,
    EncounterAdjust,
    EncounterGenerate,
    KnowledgeEdgeCreate,
    KnowledgeNodeCreate,
    LibraryEntryCreate,
    LibraryEntryUpdate,
    ShopCreate,
    StockUpdate,
    TravelPlanCreate,
)
from app.services.audit import record_audit

campaign_router = APIRouter()
presentation_router = APIRouter()


def audit_created(
    db: DatabaseSession,
    *,
    master: CampaignMaster,
    current_user: CurrentUser,
    entity_type: str,
    entity_id: uuid.UUID,
    name: str,
) -> None:
    record_audit(
        db,
        campaign_id=master.campaign.id,
        actor_user_id=current_user.id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=f"{entity_type}.created",
        after_data={"name": name},
    )


def library_payload(entry: LibraryEntry, *, master: bool) -> dict[str, object]:
    identified = master or entry.is_identified
    return {
        "id": entry.id,
        "source_entry_id": entry.source_entry_id,
        "kind": entry.kind,
        "name": entry.name if identified else "Não identificado",
        "description": entry.description if identified else "",
        "data": entry.data if identified else {},
        "is_secret": entry.is_secret if master else False,
        "is_identified": entry.is_identified,
    }


@campaign_router.post(
    "/{campaign_id}/library",
    status_code=status.HTTP_201_CREATED,
)
async def create_library_entry(
    payload: LibraryEntryCreate,
    master: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    entry = LibraryEntry(
        campaign_id=master.campaign.id,
        **payload.model_dump(),
    )
    db.add(entry)
    await db.flush()
    audit_created(
        db,
        master=master,
        current_user=current_user,
        entity_type="library_entry",
        entity_id=entry.id,
        name=entry.name,
    )
    await db.commit()
    return library_payload(entry, master=True)


@campaign_router.get("/{campaign_id}/library")
async def list_library(
    access: CampaignAccessDependency,
    db: DatabaseSession,
) -> list[dict[str, object]]:
    query = select(LibraryEntry).where(LibraryEntry.campaign_id == access.campaign.id)
    if access.member.role != "master":
        query = query.where(LibraryEntry.is_secret.is_(False))
    entries = list((await db.scalars(query.order_by(LibraryEntry.kind, LibraryEntry.name))).all())
    return [
        library_payload(entry, master=access.member.role == "master")
        for entry in entries
    ]


@campaign_router.post(
    "/{campaign_id}/library/{entry_id}/duplicate",
    status_code=status.HTTP_201_CREATED,
)
async def duplicate_library_entry(
    entry_id: uuid.UUID,
    master: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    source = await db.scalar(
        select(LibraryEntry).where(
            LibraryEntry.id == entry_id,
            LibraryEntry.campaign_id == master.campaign.id,
        )
    )
    if source is None:
        raise AppError(404, "library_entry_not_found", "Entrada não encontrada.")
    duplicate = LibraryEntry(
        campaign_id=source.campaign_id,
        source_entry_id=source.id,
        kind=source.kind,
        name=f"{source.name} — cópia",
        description=source.description,
        data=copy.deepcopy(source.data),
        is_secret=source.is_secret,
        is_identified=source.is_identified,
    )
    db.add(duplicate)
    await db.flush()
    audit_created(
        db,
        master=master,
        current_user=current_user,
        entity_type="library_entry",
        entity_id=duplicate.id,
        name=duplicate.name,
    )
    await db.commit()
    return library_payload(duplicate, master=True)


@campaign_router.patch("/{campaign_id}/library/{entry_id}")
async def update_library_entry(
    entry_id: uuid.UUID,
    payload: LibraryEntryUpdate,
    master: CampaignMaster,
    db: DatabaseSession,
) -> dict[str, object]:
    entry = await db.scalar(
        select(LibraryEntry).where(
            LibraryEntry.id == entry_id,
            LibraryEntry.campaign_id == master.campaign.id,
        )
    )
    if entry is None:
        raise AppError(404, "library_entry_not_found", "Entrada não encontrada.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, copy.deepcopy(value))
    await db.commit()
    return library_payload(entry, master=True)


@campaign_router.post("/{campaign_id}/shops", status_code=status.HTTP_201_CREATED)
async def create_shop(
    payload: ShopCreate,
    master: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    shop = Shop(campaign_id=master.campaign.id, **payload.model_dump())
    db.add(shop)
    await db.flush()
    audit_created(
        db,
        master=master,
        current_user=current_user,
        entity_type="shop",
        entity_id=shop.id,
        name=shop.name,
    )
    await db.commit()
    return {"id": shop.id, **payload.model_dump()}


@campaign_router.put("/{campaign_id}/shops/{shop_id}/stock")
async def update_shop_stock(
    shop_id: uuid.UUID,
    payload: StockUpdate,
    master: CampaignMaster,
    db: DatabaseSession,
) -> dict[str, object]:
    shop = await db.scalar(
        select(Shop).where(Shop.id == shop_id, Shop.campaign_id == master.campaign.id)
    )
    entry = await db.scalar(
        select(LibraryEntry).where(
            LibraryEntry.id == payload.library_entry_id,
            LibraryEntry.campaign_id == master.campaign.id,
        )
    )
    if shop is None or entry is None:
        raise AppError(404, "shop_or_entry_not_found", "Loja ou entrada não encontrada.")
    stock = await db.scalar(
        select(ShopStock).where(
            ShopStock.shop_id == shop.id,
            ShopStock.library_entry_id == entry.id,
        )
    )
    if stock is None:
        stock = ShopStock(
            shop_id=shop.id,
            library_entry_id=entry.id,
            **payload.model_dump(exclude={"library_entry_id"}),
        )
        db.add(stock)
    else:
        stock.quantity = payload.quantity
        stock.price_gp = payload.price_gp
        stock.is_hidden = payload.is_hidden
    await db.commit()
    return {"shop_id": shop.id, "entry_name": entry.name, **payload.model_dump()}


@campaign_router.get("/{campaign_id}/shops")
async def list_shops(
    access: CampaignAccessDependency,
    db: DatabaseSession,
) -> list[dict[str, object]]:
    query = select(Shop).where(Shop.campaign_id == access.campaign.id)
    if access.member.role != "master":
        query = query.where(Shop.is_secret.is_(False))
    shops = list((await db.scalars(query.order_by(Shop.name))).all())
    response: list[dict[str, object]] = []
    for shop in shops:
        stock_rows = (
            await db.execute(
                select(ShopStock, LibraryEntry)
                .join(LibraryEntry, LibraryEntry.id == ShopStock.library_entry_id)
                .where(ShopStock.shop_id == shop.id)
            )
        ).all()
        stock = [
            {
                "library_entry_id": row.id,
                "name": row.name if row.is_identified or access.member.role == "master"
                else "Não identificado",
                "quantity": item.quantity,
                "price_gp": item.price_gp,
            }
            for item, row in stock_rows
            if access.member.role == "master"
            or (not item.is_hidden and not row.is_secret)
        ]
        response.append(
            {
                "id": shop.id,
                "name": shop.name,
                "owner_name": shop.owner_name,
                "region": shop.region,
                "opening_hours": shop.opening_hours,
                "stock": stock,
            }
        )
    return response


@campaign_router.post("/{campaign_id}/creatures", status_code=status.HTTP_201_CREATED)
async def create_creature(
    payload: CreatureCreate,
    master: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    creature = Creature(campaign_id=master.campaign.id, **payload.model_dump())
    db.add(creature)
    await db.flush()
    audit_created(
        db,
        master=master,
        current_user=current_user,
        entity_type="creature",
        entity_id=creature.id,
        name=creature.name,
    )
    await db.commit()
    return {"id": creature.id, "source_creature_id": None, **payload.model_dump()}


@campaign_router.get("/{campaign_id}/creatures")
async def list_creatures(
    access: CampaignAccessDependency,
    db: DatabaseSession,
) -> list[dict[str, object]]:
    query = select(Creature).where(Creature.campaign_id == access.campaign.id)
    if access.member.role != "master":
        query = query.where(Creature.is_secret.is_(False))
    creatures = list((await db.scalars(query.order_by(Creature.name))).all())
    return [
        {
            "id": creature.id,
            "source_creature_id": creature.source_creature_id,
            "name": creature.name,
            "armor_class": creature.armor_class,
            "hit_points": creature.hit_points,
            "challenge_rating": creature.challenge_rating,
            "encounter_weight": creature.encounter_weight,
            "biomes": creature.biomes,
            "equipment": (
                creature.equipment
                if access.member.role == "master"
                else sanitize_public_payload(creature.equipment)
            ),
            "treasure": (
                creature.treasure
                if access.member.role == "master"
                else sanitize_public_payload(creature.treasure)
            ),
            "data": (
                creature.data
                if access.member.role == "master"
                else sanitize_public_payload(creature.data)
            ),
        }
        for creature in creatures
    ]


@campaign_router.post(
    "/{campaign_id}/creatures/{creature_id}/duplicate",
    status_code=status.HTTP_201_CREATED,
)
async def duplicate_creature(
    creature_id: uuid.UUID,
    master: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    source = await db.scalar(
        select(Creature).where(
            Creature.id == creature_id,
            Creature.campaign_id == master.campaign.id,
        )
    )
    if source is None:
        raise AppError(404, "creature_not_found", "Criatura não encontrada.")
    duplicate = Creature(
        campaign_id=source.campaign_id,
        source_creature_id=source.id,
        name=f"{source.name} — cópia",
        armor_class=source.armor_class,
        hit_points=source.hit_points,
        challenge_rating=source.challenge_rating,
        encounter_weight=source.encounter_weight,
        biomes=copy.deepcopy(source.biomes),
        equipment=copy.deepcopy(source.equipment),
        treasure=copy.deepcopy(source.treasure),
        data=copy.deepcopy(source.data),
        is_secret=source.is_secret,
    )
    db.add(duplicate)
    await db.flush()
    audit_created(
        db,
        master=master,
        current_user=current_user,
        entity_type="creature",
        entity_id=duplicate.id,
        name=duplicate.name,
    )
    await db.commit()
    return {
        "id": duplicate.id,
        "source_creature_id": source.id,
        "name": duplicate.name,
    }


@campaign_router.patch("/{campaign_id}/creatures/{creature_id}")
async def update_creature(
    creature_id: uuid.UUID,
    payload: CreatureUpdate,
    master: CampaignMaster,
    db: DatabaseSession,
) -> dict[str, object]:
    creature = await db.scalar(
        select(Creature).where(
            Creature.id == creature_id,
            Creature.campaign_id == master.campaign.id,
        )
    )
    if creature is None:
        raise AppError(404, "creature_not_found", "Criatura não encontrada.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(creature, field, copy.deepcopy(value))
    await db.commit()
    return {
        "id": creature.id,
        "source_creature_id": creature.source_creature_id,
        **payload.model_dump(exclude_unset=True),
    }


@campaign_router.post(
    "/{campaign_id}/encounters/generate",
    status_code=status.HTTP_201_CREATED,
)
async def generate_encounter(
    payload: EncounterGenerate,
    master: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    all_creatures = list(
        (
            await db.scalars(
                select(Creature).where(Creature.campaign_id == master.campaign.id)
            )
        ).all()
    )
    compatible = [
        {
            "id": creature.id,
            "name": creature.name,
            "challenge_rating": creature.challenge_rating,
            "weight": creature.encounter_weight,
        }
        for creature in all_creatures
        if payload.biome.lower() in {biome.lower() for biome in creature.biomes}
    ]
    try:
        generated = generate_weighted_encounter(
            creatures=compatible,
            danger=payload.danger,
            seed=payload.seed,
            maximum_creatures=payload.maximum_creatures,
        )
    except ValueError as error:
        raise AppError(422, "encounter_generation_failed", str(error)) from error
    encounter = Encounter(
        campaign_id=master.campaign.id,
        biome=payload.biome,
        weather=payload.weather,
        time_of_day=payload.time_of_day,
        danger=payload.danger,
        estimated_difficulty=str(generated["estimated_difficulty"]),
        difficulty_is_estimate=True,
        seed=payload.seed,
        creatures=generated["creatures"],
        history=[{"event": "generated", "seed": payload.seed}],
    )
    db.add(encounter)
    await db.flush()
    audit_created(
        db,
        master=master,
        current_user=current_user,
        entity_type="encounter",
        entity_id=encounter.id,
        name=f"Encontro em {payload.biome}",
    )
    await db.commit()
    return {"id": encounter.id, "status": encounter.status, **generated}


@campaign_router.patch("/{campaign_id}/encounters/{encounter_id}")
async def adjust_encounter(
    encounter_id: uuid.UUID,
    payload: EncounterAdjust,
    master: CampaignMaster,
    db: DatabaseSession,
) -> dict[str, object]:
    encounter = await db.scalar(
        select(Encounter).where(
            Encounter.id == encounter_id,
            Encounter.campaign_id == master.campaign.id,
        )
    )
    if encounter is None:
        raise AppError(404, "encounter_not_found", "Encontro não encontrado.")
    if payload.estimated_difficulty is not None:
        encounter.estimated_difficulty = payload.estimated_difficulty
    if payload.status is not None:
        encounter.status = payload.status
    if payload.creatures is not None:
        encounter.creatures = copy.deepcopy(payload.creatures)
    if payload.history_entry is not None:
        encounter.history = [*encounter.history, copy.deepcopy(payload.history_entry)]
    await db.commit()
    return {
        "id": encounter.id,
        "estimated_difficulty": encounter.estimated_difficulty,
        "difficulty_is_estimate": True,
        "status": encounter.status,
        "creatures": encounter.creatures,
        "history": encounter.history,
    }


async def character_load(db: DatabaseSession, character: Character) -> dict[str, object]:
    items = list(
        (
            await db.scalars(
                select(ItemInstance)
                .options(
                    joinedload(ItemInstance.template_version).joinedload(
                        ItemTemplateVersion.template
                    )
                )
                .where(ItemInstance.character_id == character.id)
            )
        ).all()
    )
    weight = sum(
        (
            Decimal(item.template_version.template.weight_kg)
            * Decimal(item.quantity)
            for item in items
        ),
        Decimal(0),
    )
    return dict(
        calculate_encumbrance(
            strength=character.strength,
            current_weight_kg=weight,
            base_speed_m=Decimal(character.speed_meters),
        )
    )


@campaign_router.get("/{campaign_id}/characters/{character_id}/encumbrance")
async def get_encumbrance(
    character_id: uuid.UUID,
    access: CampaignAccessDependency,
    db: DatabaseSession,
) -> dict[str, object]:
    character = await db.scalar(
        select(Character).where(
            Character.id == character_id,
            Character.campaign_id == access.campaign.id,
        )
    )
    if character is None:
        raise AppError(404, "character_not_found", "Personagem não encontrado.")
    if access.member.role != "master" and character.owner_user_id != access.member.user_id:
        raise AppError(404, "character_not_found", "Personagem não encontrado.")
    return await character_load(db, character)


@campaign_router.post(
    "/{campaign_id}/travel-plans",
    status_code=status.HTTP_201_CREATED,
)
async def create_travel_plan(
    payload: TravelPlanCreate,
    master: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    characters = list(
        (
            await db.scalars(
                select(Character).where(
                    Character.campaign_id == master.campaign.id,
                    Character.id.in_(payload.traveler_ids),
                )
            )
        ).all()
    )
    if len(characters) != len(set(payload.traveler_ids)):
        raise AppError(422, "traveler_not_found", "Um ou mais viajantes são inválidos.")
    travelers: list[dict[str, object]] = []
    loads: dict[str, object] = {}
    for character in characters:
        load = await character_load(db, character)
        loads[str(character.id)] = load
        travelers.append(
            {
                "character_id": character.id,
                "speed_m": load["current_speed_m"],
            }
        )
    result = plan_travel(
        distance_km=payload.distance_km,
        pace=payload.pace,
        difficult_terrain=payload.difficult_terrain,
        travelers=travelers,
        travel_hours_per_day=payload.travel_hours_per_day,
    )
    factors = [
        *([f"{payload.pace}_pace"] if payload.pace != "normal" else []),
        *(["difficult_terrain"] if payload.difficult_terrain else []),
        *(["severe_weather"] if payload.severe_weather else []),
    ]
    result["loads"] = loads
    result["hidden_fatigue_dc"] = (
        fatigue_dc(factors=factors) if payload.hidden_fatigue_enabled else None
    )
    stored_result = jsonable_encoder(result)
    plan = TravelPlan(
        campaign_id=master.campaign.id,
        name=payload.name,
        origin=payload.origin,
        destination=payload.destination,
        distance_km=payload.distance_km,
        pace=payload.pace,
        difficult_terrain=payload.difficult_terrain,
        severe_weather=payload.severe_weather,
        hidden_fatigue_enabled=payload.hidden_fatigue_enabled,
        traveler_ids=[str(value) for value in payload.traveler_ids],
        result=stored_result,
    )
    db.add(plan)
    await db.flush()
    audit_created(
        db,
        master=master,
        current_user=current_user,
        entity_type="travel_plan",
        entity_id=plan.id,
        name=plan.name,
    )
    await db.commit()
    return {"id": plan.id, **result}


@campaign_router.post(
    "/{campaign_id}/knowledge/nodes",
    status_code=status.HTTP_201_CREATED,
)
async def create_knowledge_node(
    payload: KnowledgeNodeCreate,
    master: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    node = KnowledgeNode(campaign_id=master.campaign.id, **payload.model_dump())
    db.add(node)
    await db.flush()
    audit_created(
        db,
        master=master,
        current_user=current_user,
        entity_type="knowledge_node",
        entity_id=node.id,
        name=node.title,
    )
    await db.commit()
    return {"id": node.id, **payload.model_dump()}


@campaign_router.post(
    "/{campaign_id}/knowledge/edges",
    status_code=status.HTTP_201_CREATED,
)
async def create_knowledge_edge(
    payload: KnowledgeEdgeCreate,
    master: CampaignMaster,
    db: DatabaseSession,
) -> dict[str, object]:
    node_count = len(
        (
            await db.scalars(
                select(KnowledgeNode.id).where(
                    KnowledgeNode.campaign_id == master.campaign.id,
                    KnowledgeNode.id.in_(
                        [payload.source_node_id, payload.target_node_id]
                    ),
                )
            )
        ).all()
    )
    if node_count != 2:
        raise AppError(422, "knowledge_node_not_found", "Um dos nós não existe.")
    edge = KnowledgeEdge(campaign_id=master.campaign.id, **payload.model_dump())
    db.add(edge)
    await db.commit()
    await db.refresh(edge)
    return {"id": edge.id, **payload.model_dump()}


@campaign_router.get("/{campaign_id}/knowledge")
async def get_knowledge_graph(
    access: CampaignAccessDependency,
    db: DatabaseSession,
) -> dict[str, object]:
    node_query = select(KnowledgeNode).where(
        KnowledgeNode.campaign_id == access.campaign.id
    )
    edge_query = select(KnowledgeEdge).where(
        KnowledgeEdge.campaign_id == access.campaign.id
    )
    if access.member.role != "master":
        node_query = node_query.where(KnowledgeNode.is_secret.is_(False))
        edge_query = edge_query.where(KnowledgeEdge.is_secret.is_(False))
    nodes = list((await db.scalars(node_query.order_by(KnowledgeNode.title))).all())
    visible_ids = {node.id for node in nodes}
    edges = [
        edge
        for edge in (await db.scalars(edge_query)).all()
        if edge.source_node_id in visible_ids and edge.target_node_id in visible_ids
    ]
    return {
        "nodes": [
            {
                "id": node.id,
                "node_type": node.node_type,
                "title": node.title,
                "summary": node.summary,
                "data": (
                    node.data
                    if access.member.role == "master"
                    else sanitize_public_payload(node.data)
                ),
                "occurred_at": node.occurred_at,
            }
            for node in nodes
        ],
        "edges": [
            {
                "id": edge.id,
                "source_node_id": edge.source_node_id,
                "target_node_id": edge.target_node_id,
                "relation_type": edge.relation_type,
                "directed": edge.directed,
                "confidence": edge.confidence,
            }
            for edge in edges
        ],
        "timeline": [
            {"id": node.id, "title": node.title, "occurred_at": node.occurred_at}
            for node in sorted(
                (node for node in nodes if node.occurred_at is not None),
                key=lambda item: item.occurred_at,  # type: ignore[arg-type,return-value]
            )
        ],
    }


@campaign_router.post(
    "/{campaign_id}/dashboards",
    status_code=status.HTTP_201_CREATED,
)
async def create_dashboard(
    payload: DashboardCreate,
    master: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    layout = DashboardLayout(
        campaign_id=master.campaign.id,
        owner_user_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(layout)
    await db.flush()
    audit_created(
        db,
        master=master,
        current_user=current_user,
        entity_type="dashboard",
        entity_id=layout.id,
        name=layout.name,
    )
    await db.commit()
    return {"id": layout.id, **payload.model_dump()}


@campaign_router.get("/{campaign_id}/dashboards")
async def list_dashboards(
    access: CampaignAccessDependency,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[dict[str, object]]:
    query = select(DashboardLayout).where(
        DashboardLayout.campaign_id == access.campaign.id
    )
    if access.member.role != "master":
        query = query.where(
            (DashboardLayout.owner_user_id == current_user.id)
            | (DashboardLayout.visibility.in_(["shared", "presentation"]))
        )
    layouts = list(
        (await db.scalars(query.order_by(DashboardLayout.name))).all()
    )
    return [
        {
            "id": layout.id,
            "name": layout.name,
            "template_code": layout.template_code,
            "visibility": layout.visibility,
            "cards": (
                layout.cards
                if access.member.role == "master"
                else sanitize_public_payload(layout.cards)
            ),
        }
        for layout in layouts
    ]


@presentation_router.get("/{layout_id}")
async def present_dashboard(
    layout_id: uuid.UUID,
    db: DatabaseSession,
) -> dict[str, object]:
    layout = await db.scalar(
        select(DashboardLayout).where(
            DashboardLayout.id == layout_id,
            DashboardLayout.visibility == "presentation",
        )
    )
    if layout is None:
        raise AppError(404, "presentation_not_found", "Apresentação não encontrada.")
    safe_cards = sanitize_public_payload(layout.cards)
    return {
        "id": layout.id,
        "name": layout.name,
        "template_code": layout.template_code,
        "cards": safe_cards,
    }
