"""Modelization of business models"""
import uuid
import re
import sys
from pydantic import Field, model_validator, ValidationError, computed_field, PrivateAttr, ModelWrapValidatorHandler
from src.model.base.base_modelling import TikeeMetadata, TikeeShotDefinition, TikeeShotSide
from uuid import UUID
from src.model.orm.orm_modelling import ORMTikeeShot
from typing import Any
from typing_extensions import Self
from enum import Enum




class NewTikeeShot(TikeeShotDefinition):
    """Modelize a new tikee shot to be added to DB"""

    s3_key: str = Field(
    ...,
    min_length=1,
    description="s3 path of the tikee shot; cannot be empty."
    )

    _camera_id: UUID | None = PrivateAttr(None)
    _camera_id_str: str | None = PrivateAttr(None)
    _sequence: str | None = PrivateAttr(None)
    _side: str | None = PrivateAttr(None)
    _photo_name: str | None = PrivateAttr(None)
    _photo_index: int | None = PrivateAttr(None)


    @computed_field
    @property
    def camera_id(self) -> UUID:
        """Get the camera UUID from the s3_key.
        
        Returns:
            UUID: The camera identifier
            
        Raises:
            ValueError: If the camera_id has not been set during s3_key validation
        """
        if self._camera_id is None:
            raise ValueError("camera_id not set - s3_key validation must have failed")
        return self._camera_id

    @computed_field
    @property
    def sequence(self) -> str:
        """Get the sequence number from the s3_key.
        
        Returns:
            str: The sequence identifier
            
        Raises:
            ValueError: If the sequence has not been set during s3_key validation
        """
        if self._sequence is None:
            raise ValueError("sequence not set - s3_key validation must have failed")
        return self._sequence

    @computed_field
    @property
    def side(self) -> str:
        """Get the side identifier from the s3_key.
        
        Returns:
            str: The side identifier (left, right, or stitched)
            
        Raises:
            ValueError: If the side has not been set during s3_key validation
        """
        if self._side is None:
            raise ValueError("side not set - s3_key validation must have failed")
        return self._side

    @computed_field
    @property
    def photo_name(self) -> str:
        """Get the photo filename from the s3_key.
        
        Returns:
            str: The photo filename
            
        Raises:
            ValueError: If the photo_name has not been set during s3_key validation
        """
        if self._photo_name is None:
            raise ValueError("photo_name not set - s3_key validation must have failed")
        return self._photo_name

    @computed_field
    @property
    def photo_index(self) -> int | None:
        """Get the photo index from the s3_key.
        
        Returns:
            int | None: The photo index if present in the filename, None otherwise
        """
        return self._photo_index


    @model_validator(mode='wrap')
    @classmethod
    def validate_and_parse_s3_path(cls, data: Any, handler: ModelWrapValidatorHandler[Self]):
        """Parse and validate the s3_key path structure.
        
        This validator ensures the s3_key follows the expected format and extracts its components.
        
        Args:
            data: The input data containing the s3_key
            handler: The model validator handler
            
        Returns:
            Self: The validated model instance
            
        Raises:
            ValueError: If the s3_key format is invalid or components cannot be extracted
        """
        try:
            res = handler(data)
        except ValueError:
            parts = data.get('s3_key','').strip().split('/')
            if len(parts) != 4:
                raise ValueError('s3_key must have 4 parts: <uuid>/<sequence>/<side>/<filename>')
            camera_id_str, sequence, side, filename = parts
            original_error = sys.exc_info()[1]
            raise ValueError(f"Error processing s3_key for camera '{camera_id_str}': {original_error}") from original_error
        parts = data.get('s3_key','').strip().split('/')
        if len(parts) != 4:
            raise ValueError('s3_key must have 4 parts: <uuid>/<sequence>/<side>/<filename>')
        camera_id_str, sequence, side, filename = parts
        res._camera_id_str = camera_id_str
        res._sequence = sequence
        res._side = side
        res._photo_name = filename

        return res
        
    @model_validator(mode="after")
    @classmethod
    def validate_members_of_s3_path(cls, v):
        """Validate the extracted components of the s3_key path.
        
        This validator ensures all components of the s3_key are valid:
        - camera_id must be a valid UUID
        - sequence must be numeric
        - side must be a valid TikeeShotSide enum value
        - photo_name must follow the expected format
        
        Args:
            v: The model instance to validate
            
        Returns:
            Self: The validated model instance
            
        Raises:
            ValueError: If any component of the s3_key is invalid
        """
        # Validate camera_id
        try:
            v._camera_id = UUID(v._camera_id_str)
        except ValueError:
            raise ValueError(f"Error processing s3_key for camera {v._camera_id_str}': Invalid UUID in s3_key")

        # Validate sequence
        if not re.fullmatch(r'\d+', v._sequence):
            raise ValueError(f"Error processing s3_key for camera {v._camera_id_str}: Sequence must be digits")

        # Validate side
        try:
            v._side = TikeeShotSide(v._side).value
        except ValueError:
            raise ValueError(f"Error processing s3_key for camera {v._camera_id_str}: Side must be one of: {', '.join(side.value for side in TikeeShotSide)}")

        # Validate and extract photo name and index
        match = re.fullmatch(r'my_photo(?:(\d+))?\.jpg', v._photo_name)
        if not match:
            raise ValueError(f"Error processing s3_key for camera {v._camera_id_str}: Filename must be in the format \"my_photo.jpg\" or \"my_photo[int].jpg\"")

        v._photo_index = int(match.group(1)) if match.group(1) else None

        return v


    def to_orm(self) -> ORMTikeeShot:
        """Convert the business model to an ORM model.
        
        Returns:
            ORMTikeeShot: The ORM representation of the tikee shot
        """
        model_dict = self.model_dump()
        for key in ['metadata', 's3_key']:
            model_dict.pop(key, None)
        return ORMTikeeShot(
            PK=f"{self.camera_id}#{self.sequence}",
            SK=f"{self.photo_index}#{self.side}",
            **model_dict,
            **(self.metadata.model_dump() if self.metadata is not None else {})
        )
