import pytest
import json
from uuid import UUID
from datetime import datetime
from moto import mock_aws

from src.model.business.business_modelling import NewTikeeShot, TikeeShotSide
from src.services.tikee_shot_service import TikeeShotServices
from src.lambdas.lambda_create_shot.lambda_create_shot import lambda_handler

@pytest.fixture
def valid_event():
    """Fixture providing a valid event with required data"""
    camera_uuid = "12345678-1234-5678-1234-567812345678"
    sequence = "12345678"
    return {
        "body": json.dumps({
            "s3_key": f"{camera_uuid}/{sequence}/left/my_photo1.jpg",
            "resolution": "1920x1080",
            "file_size": 1024,
            "shooting_date": "2024-01-01T12:00:00"
        })
    }

@mock_aws
def test_create_new_shot_no_existing_shot(tikee_shot_table, valid_event):
    """Test creating a new shot when no other shot exists in the database"""
    # Setup
    table = tikee_shot_table.create_tikee_shot_table()
    
    # Execute
    response = lambda_handler(valid_event, None)
    
    # Verify
    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["message"] == "Insertion successful"
    assert body["data"]["camera_id"] == "12345678-1234-5678-1234-567812345678"
    assert body["data"]["sequence"] == "12345678"
    assert body["data"]["side"] == "left"
    assert body["data"]["resolution"] == "1920x1080"

@mock_aws
def test_create_new_shot_with_matching_resolution(tikee_shot_table, valid_event):
    """Test creating a new shot when other side exists with same resolution"""
    # Setup
    table = tikee_shot_table.create_tikee_shot_table()
    service = TikeeShotServices()
    
    # Create the right side shot first
    camera_uuid = UUID("12345678-1234-5678-1234-567812345678")
    sequence = "12345678"
    existing_shot = NewTikeeShot(
        s3_key=f"{camera_uuid}/{sequence}/right/my_photo1.jpg",
        resolution="1920x1080",  # Same resolution
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    service.create(existing_shot)
    
    # Execute - Create the left side shot
    response = lambda_handler(valid_event, None)
    
    # Verify
    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["message"] == "Insertion successful"
    assert body["data"]["side"] == "left"

@mock_aws
def test_create_new_shot_with_mismatched_resolution(tikee_shot_table, valid_event):
    """Test creating a new shot when other side exists with different resolution"""
    # Setup
    table = tikee_shot_table.create_tikee_shot_table()
    service = TikeeShotServices()
    
    # Create the right side shot first with different resolution
    camera_uuid = UUID("12345678-1234-5678-1234-567812345678")
    sequence = "12345678"
    existing_shot = NewTikeeShot(
        s3_key=f"{camera_uuid}/{sequence}/right/my_photo1.jpg",
        resolution="3840x2160",  # Different resolution
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    service.create(existing_shot)
    
    # Execute - Try to create the left side shot
    response = lambda_handler(valid_event, None)
    
    # Verify
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "Resolution mismatch" in body["message"]

@mock_aws
def test_create_new_shot_with_same_side_existing(tikee_shot_table, valid_event):
    """Test creating a new shot when same side already exists"""
    # Setup
    table = tikee_shot_table.create_tikee_shot_table()
    service = TikeeShotServices()
    
    # Create the left side shot first
    camera_uuid = UUID("12345678-1234-5678-1234-567812345678")
    sequence = "12345678"
    existing_shot = NewTikeeShot(
        s3_key=f"{camera_uuid}/{sequence}/left/my_photo1.jpg",
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    service.create(existing_shot)
    
    # Execute - Try to create another left side shot
    response = lambda_handler(valid_event, None)
    
    # Verify - Should succeed as the function doesn't prevent duplicates
    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["message"] == "Insertion successful"

@mock_aws
def test_create_new_shot_invalid_data(tikee_shot_table):
    """Test creating a new shot with invalid data"""
    # Setup
    table = tikee_shot_table.create_tikee_shot_table()
    
    # Invalid event with missing required fields
    invalid_event = {
        "body": json.dumps({
            "s3_key": "invalid-uuid/12345/left/my_photo.jpg",  # Invalid UUID format
            "file_size": 1024
            # Missing resolution and shooting_date
        })
    }
    
    # Execute
    response = lambda_handler(invalid_event, None)
    
    # Verify
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["message"] == "Validation failed"
    assert "errors" in body

@mock_aws
def test_create_new_shot_malformed_json(tikee_shot_table):
    """Test creating a new shot with malformed JSON in the event body"""
    # Setup
    table = tikee_shot_table.create_tikee_shot_table()
    
    # Event with malformed JSON
    invalid_event = {
        "body": "{"  # Incomplete JSON
    }
    
    # Execute
    response = lambda_handler(invalid_event, None)
    
    # Verify
    assert response["statusCode"] == 400