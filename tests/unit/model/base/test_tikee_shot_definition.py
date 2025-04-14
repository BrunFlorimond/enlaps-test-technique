from decimal import Decimal
from datetime import datetime
import pytest
from src.model.base.base_modelling import TikeeShotDefinition, TikeeMetadata

def test_tikee_shot_definition_creation_with_all_fields():
    """Test creating TikeeShotDefinition with all fields populated"""
    metadata = TikeeMetadata(
        gps_latitude="48.8584",
        gps_longitude="2.2945"
    )
    
    shot = TikeeShotDefinition(
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0),
        metadata=metadata
    )
    
    assert shot.resolution == "1920x1080"
    assert shot.file_size == 1024
    assert shot.shooting_date == datetime(2024, 1, 1, 12, 0)
    assert shot.metadata == metadata
    assert shot.metadata.gps_latitude == Decimal("48.8584")
    assert shot.metadata.gps_longitude == Decimal("2.2945")

def test_tikee_shot_definition_creation_without_metadata():
    """Test creating TikeeShotDefinition without optional metadata"""
    shot = TikeeShotDefinition(
        resolution="1920x1080",
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    
    assert shot.resolution == "1920x1080"
    assert shot.file_size == 1024
    assert shot.shooting_date == datetime(2024, 1, 1, 12, 0)
    assert shot.metadata is None

@pytest.mark.parametrize("resolution", [
    "1920x1080",
    "3840x2160",
    "1280x720",
    "1x1"
])
def test_tikee_shot_definition_valid_resolution(resolution):
    """Test that valid resolution formats are accepted using parametrize"""
    shot = TikeeShotDefinition(
        resolution=resolution,
        file_size=1024,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    assert shot.resolution == resolution

@pytest.mark.parametrize("resolution", [
    "1920x",         # missing second number
    "x1080",         # missing first number
    "1920-1080",     # wrong separator
    "1920x1080x720", # too many dimensions
    "abcxdef",       # non-numeric
    "1920.5x1080",   # decimal numbers
    ""               # empty string
])
def test_tikee_shot_definition_invalid_resolution(resolution):
    """Test that invalid resolution formats raise ValueError using parametrize"""
    with pytest.raises(ValueError, match='resolution must be in the format "intxint"'):
        TikeeShotDefinition(
            resolution=resolution,
            file_size=1024,
            shooting_date=datetime(2024, 1, 1, 12, 0)
        )

def test_tikee_shot_definition_invalid_file_size():
    """Test that negative file size raises validation error"""
    with pytest.raises(ValueError):
        TikeeShotDefinition(
            resolution="1920x1080",
            file_size=-1,
            shooting_date=datetime(2024, 1, 1, 12, 0)
        )

def test_tikee_shot_definition_zero_file_size():
    """Test that zero file size is accepted"""
    shot = TikeeShotDefinition(
        resolution="1920x1080",
        file_size=0,
        shooting_date=datetime(2024, 1, 1, 12, 0)
    )
    assert shot.file_size == 0 