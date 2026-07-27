from typing import Literal, TypedDict

from app.domain.rules.class_progression import CLASS_DEFINITIONS, ClassId

SubclassId = Literal[
    "path_of_the_berserker",
    "college_of_lore",
    "life_domain",
    "circle_of_the_land",
    "champion",
    "way_of_the_open_hand",
    "oath_of_devotion",
    "hunter",
    "thief",
    "draconic_bloodline",
    "the_fiend",
    "school_of_evocation",
]


class SubclassDefinition(TypedDict):
    id: SubclassId
    label: str
    choice_level: int


class SubclassOption(TypedDict):
    id: SubclassId
    label: str
    source: Literal["srd_5_1"]


class SubclassChoiceSimulation(TypedDict):
    class_id: ClassId
    class_label: str
    target_class_level: int
    choice_level: int
    choice_available: bool
    selection_required: bool
    selected_subclass_id: SubclassId | None
    selected_subclass_label: str | None
    available_subclasses: list[SubclassOption]


SRD_SUBCLASSES: dict[ClassId, SubclassDefinition] = {
    "barbarian": {
        "id": "path_of_the_berserker",
        "label": "Caminho do Berserker",
        "choice_level": 3,
    },
    "bard": {
        "id": "college_of_lore",
        "label": "Colégio do Conhecimento",
        "choice_level": 3,
    },
    "cleric": {
        "id": "life_domain",
        "label": "Domínio da Vida",
        "choice_level": 1,
    },
    "druid": {
        "id": "circle_of_the_land",
        "label": "Círculo da Terra",
        "choice_level": 2,
    },
    "fighter": {
        "id": "champion",
        "label": "Campeão",
        "choice_level": 3,
    },
    "monk": {
        "id": "way_of_the_open_hand",
        "label": "Caminho da Mão Aberta",
        "choice_level": 3,
    },
    "paladin": {
        "id": "oath_of_devotion",
        "label": "Juramento de Devoção",
        "choice_level": 3,
    },
    "ranger": {
        "id": "hunter",
        "label": "Caçador",
        "choice_level": 3,
    },
    "rogue": {
        "id": "thief",
        "label": "Ladrão",
        "choice_level": 3,
    },
    "sorcerer": {
        "id": "draconic_bloodline",
        "label": "Linhagem Dracônica",
        "choice_level": 1,
    },
    "warlock": {
        "id": "the_fiend",
        "label": "Patrono Corruptor",
        "choice_level": 1,
    },
    "wizard": {
        "id": "school_of_evocation",
        "label": "Escola de Evocação",
        "choice_level": 2,
    },
}


def validate_subclass_selection(
    *,
    class_id: ClassId,
    target_class_level: int,
    selected_subclass_id: SubclassId | None,
) -> None:
    if target_class_level < 1 or target_class_level > 20:
        raise ValueError("O nível alvo da classe deve estar entre 1 e 20.")

    definition = SRD_SUBCLASSES[class_id]
    if selected_subclass_id is not None and target_class_level < definition["choice_level"]:
        raise ValueError("A subclasse não pode ser escolhida antes do nível previsto.")
    if (
        selected_subclass_id is not None
        and selected_subclass_id != definition["id"]
    ):
        raise ValueError("A subclasse selecionada não pertence à classe informada.")


def simulate_subclass_choice(
    *,
    class_id: ClassId,
    target_class_level: int,
    selected_subclass_id: SubclassId | None = None,
) -> SubclassChoiceSimulation:
    validate_subclass_selection(
        class_id=class_id,
        target_class_level=target_class_level,
        selected_subclass_id=selected_subclass_id,
    )
    definition = SRD_SUBCLASSES[class_id]
    choice_available = target_class_level >= definition["choice_level"]

    return {
        "class_id": class_id,
        "class_label": CLASS_DEFINITIONS[class_id]["label"],
        "target_class_level": target_class_level,
        "choice_level": definition["choice_level"],
        "choice_available": choice_available,
        "selection_required": choice_available and selected_subclass_id is None,
        "selected_subclass_id": selected_subclass_id,
        "selected_subclass_label": (
            definition["label"] if selected_subclass_id is not None else None
        ),
        "available_subclasses": [
            {
                "id": definition["id"],
                "label": definition["label"],
                "source": "srd_5_1",
            }
        ],
    }
