import pytest
import boto3
from moto import mock_aws
from uuid import UUID
from datetime import datetime

from src.services.tikee_shot_service import TikeeShotServices
from src.model.business.business_modelling import NewTikeeShot, TikeeShotSide
from src.model.orm.orm_modelling import ORMTikeeShot, ORMTikeeShotIdentifier


@mock_aws
def test_create_tikee_shot(tikee_shot_table):
    """Test creating a new tikee shot"""

    table = tikee_shot_table.create_tikee_shot_table()
    service = TikeeShotServices()
    
    # Create a new tikee shot
    camera_uuid = UUID('12345678-1234-5678-1234-567812345678')
    sequence = 12345678
    new_shot = NewTikeeShot(
        s3_key=f"{str(camera_uuid)}/{str(sequence)}/{TikeeShotSide.LEFT.value}/my_photo.jpg",
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    
    created_shot = service.create(new_shot)
    
    # Verify the created shot
    assert created_shot is not None
    assert created_shot.camera_id == camera_uuid
    assert created_shot.sequence == str(sequence)
    assert created_shot.photo_index is None
    assert created_shot.photo_name == "my_photo.jpg"
    assert created_shot.side == TikeeShotSide.LEFT
    assert created_shot.resolution == "1920x1080"
    assert created_shot.file_size == 1024

@mock_aws
def test_get_tikee_shot_by_id(tikee_shot_table):
    """Test retrieving a tikee shot by its identifier"""
    table = tikee_shot_table.create_tikee_shot_table()
    service = TikeeShotServices()
    
    # First create a shot
    camera_uuid = UUID('12345678-1234-5678-1234-567812345678')
    sequence = 12345678
    new_shot = NewTikeeShot(
        s3_key=f"{str(camera_uuid)}/{str(sequence)}/{TikeeShotSide.LEFT.value}/my_photo.jpg",
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    created_shot = service.create(new_shot)
    
    # Create identifier and retrieve the shot
    identifier = ORMTikeeShotIdentifier(
        PK=created_shot.PK,
        SK=created_shot.SK
    )
    retrieved_shot = service.get_tikee_shot_by_id(identifier)
    
    # Verify the retrieved shot
    assert retrieved_shot is not None
    assert retrieved_shot.camera_id == camera_uuid
    assert retrieved_shot.sequence == str(sequence)
    assert retrieved_shot.photo_index is None
    assert retrieved_shot.photo_name == "my_photo.jpg"
    assert retrieved_shot.side == TikeeShotSide.LEFT
    assert retrieved_shot.resolution == "1920x1080"
    assert retrieved_shot.file_size == 1024

@mock_aws
def test_get_tikee_shot_of_camera_by_id(tikee_shot_table):
    """Test retrieving all tikee shots for a specific camera"""
    table = tikee_shot_table.create_tikee_shot_table()
    service = TikeeShotServices()
    
    # Create multiple shots for the same camera
    camera_uuid = UUID('12345678-1234-5678-1234-567812345678')
    sequences = ["12345678", "12345679"]
    sides = [TikeeShotSide.LEFT, TikeeShotSide.RIGHT]
    
    created_shots = []
    for sequence in sequences:
        for side in sides:
            new_shot = NewTikeeShot(
                s3_key=f"{str(camera_uuid)}/{sequence}/{side.value}/my_photo.jpg",
                resolution="1920x1080",
                file_size=1024,
                shooting_date=datetime(2024, 1, 1, 12, 0)
            )
            created_shots.append(service.create(new_shot))
    
    # Retrieve all shots for the camera
    retrieved_shots = service.get_tikee_shot_of_camera_by_id(camera_uuid)
    
    # Verify the retrieved shots
    assert len(retrieved_shots) == 4  # 2 sequences * 2 sides
    for shot in retrieved_shots:
        assert shot.camera_id == camera_uuid
        assert shot.sequence in sequences
        assert shot.side in sides

@mock_aws
def test_get_tikee_shot_of_sequence(tikee_shot_table):
    """Test retrieving all tikee shots for a specific sequence"""
    table = tikee_shot_table.create_tikee_shot_table()
    service = TikeeShotServices()
    
    # Create shots for a specific sequence
    camera_uuid = UUID('12345678-1234-5678-1234-567812345678')
    sequence = "12345678"
    sides = [TikeeShotSide.LEFT, TikeeShotSide.RIGHT]
    photo_index = 1
    created_shots = []
    for side in sides:
        new_shot = NewTikeeShot(
            s3_key=f"{str(camera_uuid)}/{sequence}/{side.value}/my_photo{str(photo_index)}.jpg",
            resolution="1920x1080",
            file_size=1024,
            shooting_date=datetime(2024, 1, 1, 12, 0)
        )
        created_shots.append(service.create(new_shot))
    
    # Retrieve shots for the sequence
    retrieved_shots = service.get_tikee_shot_of_sequence(camera_uuid, sequence)
    
    # Verify the retrieved shots
    assert len(retrieved_shots) == 2  # 2 sides
    for shot in retrieved_shots:
        assert shot.camera_id == camera_uuid
        assert shot.sequence == sequence
        assert shot.side in sides
        assert shot.photo_index == photo_index

@mock_aws
def test_get_tikee_shot_of_photo_index(tikee_shot_table):
    """Test retrieving tikee shots for a specific photo index"""
    table = tikee_shot_table.create_tikee_shot_table()
    service = TikeeShotServices()
    
    # Create shots with specific photo indices
    camera_uuid = UUID('12345678-1234-5678-1234-567812345678')
    sequence = "12345678"
    photo_index = range(1,12)
    sides = [TikeeShotSide.LEFT, TikeeShotSide.RIGHT]
    
    created_shots = []
    for side in sides:
        for pic_index in photo_index:
            new_shot = NewTikeeShot(
                s3_key=f"{str(camera_uuid)}/{sequence}/{side.value}/my_photo{str(pic_index)}.jpg",
                resolution="1920x1080",
                file_size=1024,
                shooting_date=datetime(2024, 1, 1, 12, 0),
                photo_index=photo_index
            )
            created_shots.append(service.create(new_shot))
    
    # Retrieve shots for the photo index
    retrieved_shots = service.get_tikee_shot_of_photo_index(camera_uuid, sequence, 7)
    
    # Verify the retrieved shots
    assert len(retrieved_shots) == 2  # 2 sides
    for shot in retrieved_shots:
        assert shot.camera_id == camera_uuid
        assert shot.sequence == sequence
        assert shot.photo_index == 7
        assert shot.side in sides

@mock_aws
def test_get_tikee_shot(tikee_shot_table):
    """Test retrieving a specific tikee shot by all parameters"""
    table = tikee_shot_table.create_tikee_shot_table()
    service = TikeeShotServices()
    
    # Create a specific shot
    camera_uuid = UUID('12345678-1234-5678-1234-567812345678')
    sequence = "12345678"
    photo_index = 1
    side = TikeeShotSide.LEFT
    
    new_shot = NewTikeeShot(
        s3_key=f"{str(camera_uuid)}/{sequence}/{side.value}/my_photo{str(photo_index)}.jpg",
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0),
        photo_index=photo_index
    )
    created_shot = service.create(new_shot)
    
    # Retrieve the specific shot
    retrieved_shot = service.get_tikee_shot(camera_uuid, sequence, photo_index, side)
    
    # Verify the retrieved shot
    assert retrieved_shot is not None
    assert retrieved_shot.camera_id == camera_uuid
    assert retrieved_shot.sequence == sequence
    assert retrieved_shot.photo_index == photo_index
    assert retrieved_shot.side == side
    
    # Test retrieving non-existent shot
    non_existent = service.get_tikee_shot(camera_uuid, "99999999", photo_index, side)
    assert non_existent is None

@mock_aws
def test_build_pk():
    """Test the static method for building primary key"""
    service = TikeeShotServices()
    uuid = UUID('12345678-1234-5678-1234-567812345678')
    sequence = "12345678"
    
    pk = service.build_pk(uuid, sequence)
    assert pk == f"{str(uuid)}#{sequence}"

@mock_aws
def test_build_sk():
    """Test the static method for building sort key"""
    service = TikeeShotServices()
    
    # Test with all values provided
    sk1 = service.build_sk(1, TikeeShotSide.LEFT)
    assert sk1 == "1#left"
    
    # Test with None values
    sk2 = service.build_sk(None, None)
    assert sk2 == "#"
    
    # Test with mixed values
    sk3 = service.build_sk(1, None)
    assert sk3 == "1#"
    
    sk4 = service.build_sk(None, TikeeShotSide.RIGHT)
    assert sk4 == "#right"

