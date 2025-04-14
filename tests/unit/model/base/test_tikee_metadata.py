from decimal import Decimal
from src.model.base.base_modelling import TikeeMetadata
from datetime import datetime
import pytest

def test_tikee_metadata_creation_with_all_fields():
    """Test creating TikeeMetadata with all fields populated"""
    metadata = TikeeMetadata(
        gps_latitude=48.8584,
        gps_longitude=2.2945,
        gps_altitude=100.5,
        camera_model_name="Tikee Pro",
        make="Enlaps"
    )
    
    assert metadata.gps_latitude == Decimal("48.8584")
    assert metadata.gps_longitude == Decimal("2.2945")
    assert metadata.gps_altitude == Decimal("100.5")
    assert metadata.camera_model_name == "Tikee Pro"
    assert metadata.make == "Enlaps"

def test_tikee_metadata_creation_with_all_fields_as_string():
    """Test creating TikeeMetadata with all fields populated"""
    metadata = TikeeMetadata(
        gps_latitude="48.8584",
        gps_longitude="2.2945",
        gps_altitude="100.5",
        camera_model_name="Tikee Pro",
        make="Enlaps"
    )
    
    assert metadata.gps_latitude == Decimal("48.8584")
    assert metadata.gps_longitude == Decimal("2.2945")
    assert metadata.gps_altitude == Decimal("100.5")
    assert metadata.camera_model_name == "Tikee Pro"
    assert metadata.make == "Enlaps"


def test_tikee_metadata_creation_with_optional_fields():
    """Test creating TikeeMetadata with only some fields populated"""
    metadata = TikeeMetadata(
        gps_latitude=48.8584,
        camera_model_name="Tikee Pro"
    )
    
    assert metadata.gps_latitude == Decimal("48.8584")
    assert metadata.gps_longitude is None
    assert metadata.gps_altitude is None
    assert metadata.camera_model_name == "Tikee Pro"
    assert metadata.make is None

def test_tikee_metadata_creation_with_no_fields():
    """Test creating TikeeMetadata with no fields populated"""
    metadata = TikeeMetadata()
    
    assert metadata.gps_latitude is None
    assert metadata.gps_longitude is None
    assert metadata.gps_altitude is None
    assert metadata.camera_model_name is None
    assert metadata.make is None

def test_tikee_metadata_aliases():
    """Test that field aliases work correctly"""
    metadata = TikeeMetadata(
        **{"GPSLatitude": 48.8584,
        "GPSLongitude": 2.2945,
        "GPSAltitude": 100.5,
        "Camera Model Name": "Tikee Pro",
        "Make": "Enlaps"}
    )
    
    assert metadata.gps_latitude == Decimal("48.8584")
    assert metadata.gps_longitude == Decimal("2.2945")
    assert metadata.gps_altitude == Decimal("100.5")
    assert metadata.camera_model_name == "Tikee Pro"
    assert metadata.make == "Enlaps"

def test_tikee_metadata_invalid_decimal():
    """Test that TikeeMetadata raises a validation error when an invalid value is provided for gps_latitude."""
    with pytest.raises(Exception) as exc_info:
        TikeeMetadata(gps_latitude="not_a_decimal")
    assert "decimal" in str(exc_info.value).lower()