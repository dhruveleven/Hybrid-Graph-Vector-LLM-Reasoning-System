from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, model_validator


# -----------------------------
# Entity Model
# -----------------------------

class ExtractedEntity(BaseModel):
    """
    Represents a single extracted entity from a document chunk.
    """

    id: str = Field(
        ...,
        description="Unique identifier for the entity within the chunk"
    )

    type: Literal["Entity", "Event", "Concept", "Metric"] = Field(
        ...,
        description="High-level entity type (restricted vocabulary)"
    )

    subtype: Optional[str] = Field(
        None,
        description="Optional descriptive subtype (domain-agnostic)"
    )

    name: str = Field(
        ...,
        description="Human-readable name of the entity"
    )

    attributes: Dict[str, str] = Field(
        default_factory=dict,
        description="Flat key-value attributes extracted from text"
    )

    source_chunk_id: Optional[str] = None
    confidence: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)



# -----------------------------
# Relationship Model
# -----------------------------

class ExtractedRelationship(BaseModel):
    """
    Represents a relationship between two extracted entities.
    """

    source_id: str = Field(
        ...,
        description="ID of the source entity"
    )

    target_id: str = Field(
        ...,
        description="ID of the target entity"
    )

    type: Literal[
        "MENTIONS",
        "RELATED_TO",
        "ASSOCIATED_WITH",
        "CAUSES",
        "PRECEDES",
        "PART_OF",
        "MEASURED_BY",
        "EXTRACTED_FROM"
    ] = Field(
        ...,
        description="Relationship type (restricted vocabulary)"
    )
    
    source_chunk_id: Optional[str] = None
    confidence: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)

    


# -----------------------------
# Top-Level Extraction Result
# -----------------------------

class ExtractionResult(BaseModel):
    """
    Top-level container for LLM extraction output.
    """

    entities: List[ExtractedEntity] = Field(
        default_factory=list,
        description="List of extracted entities"
    )

    relationships: List[ExtractedRelationship] = Field(
        default_factory=list,
        description="List of extracted relationships"
    )

    @model_validator(mode='before')
    def validate_relationship_references(cls, data):
        """
        Ensure that all relationship source_id and target_id
        values refer to valid extracted entities.
        """
        entity_ids = {entity.get('id') for entity in data.get("entities", [])}

        for rel in data.get("relationships", []):
            if rel.get('source_id') not in entity_ids:
                raise ValueError(
                    f"Relationship source_id '{rel.get('source_id')}' "
                    f"does not match any extracted entity id"
                )
            if rel.get('target_id') not in entity_ids:
                raise ValueError(
                    f"Relationship target_id '{rel.get('target_id')}' "
                    f"does not match any extracted entity id"
                )
        return data
