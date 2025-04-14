""" Models used as based for ORM or business entities"""
from decimal import Decimal
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from datetime import datetime
from uuid import UUID
import re

class TikeeShotSide(Enum):
    LEFT = "left"
    RIGHT = "right"
    STITCHED = "stitched"

    def opposite_side(self):
        if self == TikeeShotSide.LEFT:
            return TikeeShotSide.RIGHT
        elif self == TikeeShotSide.RIGHT:
            return TikeeShotSide.LEFT
        else:
            return self


class TikeeMetadata(BaseModel):
    """Base domain modelization of Tikees MetaData"""

    model_config = ConfigDict(populate_by_name=True)

    gps_latitude: Optional[Decimal] = Field(
        None,
        description="The latitude of the Tikee",
        alias="GPSLatitude"
    )

    gps_longitude: Optional[Decimal] = Field(
        None,
        description="The longitude of the Tikee",
        alias="GPSLongitude"
    )

    gps_longitude: Optional[Decimal] = Field(
        None,
        description="The longitude of the Tikee",
        alias="GPSLongitude"
    )

    gps_altitude: Optional[Decimal] = Field(
        None,
        description="The altitude of the Tikee",
        alias="GPSAltitude"
    )

    camera_model_name: Optional[str] = Field(
        None,
        description="The name of the camera model",
        alias="Camera Model Name"
    )

    make: Optional[str] = Field(
        None,
        description="Constructor of the camera",
        alias="Make"
    )


class TikeeShotDefinition(BaseModel):
    """Base domain modelization of a Tikee Shot"""

    model_config = ConfigDict(populate_by_name=True)

    resolution: str = Field(
        ...,
        description="The latitude of the Tikee"
    )

    file_size: int = Field(
        ...,
        ge=0,
        description="the file size in bytes"
    )

    shooting_date: datetime = Field(
        ...,
        description="the date of the shooting"
    )

    metadata: Optional[TikeeMetadata] = Field(
        None,
        description="Metadata of the shot"
    )

    @field_validator('resolution')
    @classmethod
    def validate_resolution(cls, value):
        """Validate that resolution is formed as int x int"""
        if not re.match(r'^\d+x\d+$', value):
            raise ValueError('resolution must be in the format "intxint", e.g. "1920x1080"')
        return value

class TikeetShotComputedProperties(BaseModel):
    """
    Computed properties from new tikee shot
    """

    camera_id: UUID = Field(
        ...,
        description="UUID of the tikee camera"
    )

    sequence: str = Field(
        ...,
        description="Sequence id"
    )
        
    side: TikeeShotSide = Field(
        ...,
        description="Side of the Tikee shot"
    )

    photo_name: str = Field(
        ...,
        description="Filename of the photo"
    )

    photo_index: int | None = Field(
        None,
        description="Index of the tikee shot"
    )

