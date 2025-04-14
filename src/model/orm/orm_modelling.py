"""Model Database entities"""
from pydantic import Field, BaseModel
from src.model.base.base_modelling import TikeeShotDefinition, TikeeMetadata, TikeetShotComputedProperties


class ORMTikeeShotIdentifier(BaseModel):
    """ORM-facing Tikee shot primary and secondary key for persistence."""
    PK: str = Field(
        ...,
        min_length=1,
        description="PK is formed from UUID and sequence such as: 677c082c-3a1a-44d9-874a20169546c653#123456789"
    )

    SK: str = Field(
        ...,
        min_length=1,
        description="SK is formed from photo number and side such as 1#left or #left"
    )

class ORMTikeeShot(ORMTikeeShotIdentifier, TikeeShotDefinition, TikeeMetadata, TikeetShotComputedProperties):
    """ORM-facing tikee shot model for persistence."""
