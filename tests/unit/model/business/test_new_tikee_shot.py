from datetime import datetime
from decimal import Decimal
import pytest
from uuid import UUID
from src.model.business.business_modelling import NewTikeeShot
from src.model.base.base_modelling import TikeeMetadata, TikeeShotSide

def test_new_tikee_shot_creation_with_valid_data():
    """Test creating NewTikeeShot with valid data"""
    a=1
    shot = NewTikeeShot(
        s3_key="123e4567-e89b-12d3-a456-426614174000/123456/left/my_photo1.jpg",
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    
    assert isinstance(shot.camera_id, UUID)
    assert shot.sequence == "123456"
    assert shot.side == "left"
    assert shot.photo_name == "my_photo1.jpg"
    assert shot.photo_index == 1
    assert shot.resolution == "1920x1080"
    assert shot.file_size == 1024
    assert shot.shooting_date == datetime(2024, 1, 1, 12, 0)
    assert shot.metadata is None

def test_new_tikee_shot_creation_with_metadata():
    """Test creating NewTikeeShot with metadata"""
    metadata = TikeeMetadata(
        gps_latitude=48.8584,
        gps_longitude=2.2945
    )
    
    shot = NewTikeeShot(
        s3_key="123e4567-e89b-12d3-a456-426614174000/123456/left/my_photo1.jpg",
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0),
        metadata=metadata
    )
    
    assert shot.metadata == metadata
    assert shot.metadata.gps_latitude == Decimal('48.8584')
    assert shot.metadata.gps_longitude == Decimal('2.2945')

def test_new_tikee_shot_creation_with_photo_without_index():
    """Test creating NewTikeeShot with a photo that doesn't have an index"""
    shot = NewTikeeShot(
        s3_key="123e4567-e89b-12d3-a456-426614174000/123456/left/my_photo.jpg",
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    
    assert shot.photo_name == "my_photo.jpg"
    assert shot.photo_index is None

@pytest.mark.parametrize("uuid,invalid_s3_key,expected_error,uuid_in_error", [
    # Invalid UUID
    ("invalid-uuid","/123456/left/my_photo.jpg", "Invalid UUID in s3_key", True),
    # Wrong number of parts
    ("123e4567-e89b-12d3-a456-426614174000","/123456/left", "s3_key must have 4 parts", False),
    ("123e4567-e89b-12d3-a456-426614174000","/123456/left/my_photo.jpg/extra", "s3_key must have 4 parts", False),
    # Invalid sequence
    ("123e4567-e89b-12d3-a456-426614174000","/abc/left/my_photo.jpg", "Sequence must be digits", True),
    # Invalid side
    ("123e4567-e89b-12d3-a456-426614174000","/123456/invalid/my_photo.jpg", "Side must be one of: left, right, stitched", True),
    # Invalid filename
    ("123e4567-e89b-12d3-a456-426614174000","/123456/left/invalid.jpg", "Filename must be in the format", True),
])
def test_new_tikee_shot_invalid_s3_key(uuid, invalid_s3_key, expected_error, uuid_in_error):
    """Test NewTikeeShot creation with various invalid s3_key formats"""
    s3_key = uuid+invalid_s3_key
    with pytest.raises(ValueError) as exc_info:
        NewTikeeShot(
            s3_key=s3_key,
            resolution="1920x1080",
            file_size=1024,
            shooting_date=datetime(2024, 1, 1, 12, 0)
        )
    
    assert expected_error in str(exc_info.value)
    if uuid_in_error:
        assert uuid in str(exc_info.value)

def test_new_tikee_shot_invalid_resolution():
    """Test NewTikeeShot creation with invalid resolution"""
    with pytest.raises(ValueError) as exc_info:
        NewTikeeShot(
            s3_key="123e4567-e89b-12d3-a456-426614174000/123456/left/my_photo.jpg",
            resolution="invalid",
            file_size=1024,
            shooting_date=datetime(2024, 1, 1, 12, 0)
        )
    assert "resolution must be in the format" in str(exc_info.value)
    assert "123e4567-e89b-12d3-a456-426614174000" in str(exc_info.value)

def test_new_tikee_shot_invalid_file_size():
    """Test NewTikeeShot creation with invalid file size"""
    with pytest.raises(ValueError) as exc_info:
        NewTikeeShot(
            s3_key="123e4567-e89b-12d3-a456-426614174000/123456/left/my_photo.jpg",
            resolution="1920x1080",
            file_size=-1,
            shooting_date=datetime(2024, 1, 1, 12, 0)
        )
    assert "file_size" in str(exc_info.value)
    assert "123e4567-e89b-12d3-a456-426614174000" in str(exc_info.value)

def test_new_tikee_shot_to_orm():
    """Test converting NewTikeeShot to ORM model"""
    shot = NewTikeeShot(
        s3_key="123e4567-e89b-12d3-a456-426614174000/123456/left/my_photo1.jpg",
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    
    orm_shot = shot.to_orm()
    
    assert orm_shot.PK == "123e4567-e89b-12d3-a456-426614174000#123456"
    assert orm_shot.SK == "1#left"
    assert orm_shot.resolution == "1920x1080"
    assert orm_shot.file_size == 1024
    assert orm_shot.shooting_date == datetime(2024, 1, 1, 12, 0)
    assert orm_shot.camera_id == UUID("123e4567-e89b-12d3-a456-426614174000")
    assert orm_shot.sequence == '123456'
    assert orm_shot.side == TikeeShotSide.LEFT
    assert orm_shot.photo_name == "my_photo1.jpg"
    assert orm_shot.photo_index == 1


def test_new_tikee_shot_to_orm_with_metadata():
    """Test converting NewTikeeShot with metadata to ORM model"""
    metadata = TikeeMetadata(
        gps_latitude=48.8584,
        gps_longitude=2.2945
    )
    
    shot = NewTikeeShot(
        s3_key="123e4567-e89b-12d3-a456-426614174000/123456/left/my_photo1.jpg",
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0),
        metadata=metadata
    )
    
    orm_shot = shot.to_orm()
    
    assert orm_shot.gps_latitude == Decimal('48.8584')
    assert orm_shot.gps_longitude == Decimal('2.2945') 