"""Unit tests for ORM models"""
from datetime import datetime
from uuid import UUID
import pytest
from src.model.orm.orm_modelling import ORMTikeeShot, ORMTikeeShotIdentifier
from src.model.base.base_modelling import TikeeShotSide

def test_build_s3_path_with_all_fields():
    """Test building S3 path with all fields populated"""
    # Create an ORMTikeeShot instance with all required fields
    shot = ORMTikeeShot(
        PK="123e4567-e89b-12d3-a456-426614174000#123456",
        SK="1#left",
        camera_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        sequence="123456",
        side=TikeeShotSide.LEFT,
        photo_name="my_photo1.jpg",
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    
    # Test the build_s3_path method
    s3_path = shot.build_s3_path()
    
    # Verify the path is constructed correctly
    assert s3_path == "123e4567-e89b-12d3-a456-426614174000/123456/left/my_photo1.jpg"

def test_build_s3_path_with_different_side():
    """Test building S3 path with different side values"""
    # Create test cases for different sides
    test_cases = [
        (TikeeShotSide.LEFT, "left"),
        (TikeeShotSide.RIGHT, "right"),
        (TikeeShotSide.STITCHED, "stitched")
    ]
    
    for side, expected_side_value in test_cases:
        shot = ORMTikeeShot(
            PK="123e4567-e89b-12d3-a456-426614174000#123456",
            SK="1#left",
            camera_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            sequence="123456",
            side=side,
            photo_name="my_photo1.jpg",
            resolution="1920x1080",
            file_size=1024,
            shooting_date=datetime(2024, 1, 1, 12, 0)
        )
        
        s3_path = shot.build_s3_path()
        assert s3_path == f"123e4567-e89b-12d3-a456-426614174000/123456/{expected_side_value}/my_photo1.jpg"

def test_build_s3_path_with_different_sequences():
    """Test building S3 path with different sequence values"""
    # Create test cases for different sequences
    test_cases = [
        "123456",
        "987654",
        "000001",
        "999999"
    ]
    
    for sequence in test_cases:
        shot = ORMTikeeShot(
            PK="123e4567-e89b-12d3-a456-426614174000#123456",
            SK="1#left",
            camera_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            sequence=sequence,
            side=TikeeShotSide.LEFT,
            photo_name="my_photo1.jpg",
            resolution="1920x1080",
            file_size=1024,
            shooting_date=datetime(2024, 1, 1, 12, 0)
        )
        
        s3_path = shot.build_s3_path()
        assert s3_path == f"123e4567-e89b-12d3-a456-426614174000/{sequence}/left/my_photo1.jpg" 