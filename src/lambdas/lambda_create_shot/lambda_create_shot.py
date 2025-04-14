"""Lambda to create product in dynamo DB table"""

import json
import logging


from pydantic import ValidationError

from src.model.base.base_modelling import TikeeShotSide
from src.model.business.business_modelling import NewTikeeShot
from src.model.orm.orm_modelling import ORMTikeeShot
from src.services.tikee_shot_service import TikeeShotServices


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, _):
    """Lambda handler to create a tikee shot in dynamoDB table"""

    try:

        body = json.loads(event.get("body", "{}"))
        new_tikee_shot = NewTikeeShot(**body)
        tikee_shot_service = TikeeShotServices()
        photos_with_same_index = tikee_shot_service.get_tikee_shot_of_photo_index(
            new_tikee_shot.camera_id,
            new_tikee_shot.sequence,
            new_tikee_shot.photo_index,
        )
        if is_same_resolution(
            new_tikee_shot.to_orm(),
            get_other_side_photo(
                TikeeShotSide(new_tikee_shot.side), photos_with_same_index
            ),
        ):
            orm_tikee_shot = TikeeShotServices().create(new_tikee_shot)
        else:
            raise ValueError(
                f"Resolution mismatch: The other side does not have the same resolution for camera {new_tikee_shot.camera_id}."
            )

        response = {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "message": "Insertion successful",
                    "data": new_tikee_shot.model_dump(),
                },
                default=str,
            ),
        }
    except ValidationError as e:
        response = {
            "statusCode": 400,
            "body": json.dumps(
                {"message": "Validation failed", "errors": e.errors()}, default=str
            ),
        }
    except ValueError as e:
        response = {
            "statusCode": 400,
            "body": json.dumps({"message": str(e)}, default=str),
        }
    except Exception as e:
        logger.exception("An error occurred")
        response = {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"}, default=str),
        }

    return response


def get_other_side_photo(
    current_side: TikeeShotSide, tikee_shots: list[ORMTikeeShot]
) -> ORMTikeeShot | None:
    """
    Returns the tikee shot that belongs to the opposite side of the current shot.

    This function searches through the provided list of tikee shots and returns the first shot
    whose side is opposite to the given current_side. If no such shot exists, the function returns None.

    Args:
        current_side (TikeeShotSide): The side of the current tikee shot.
        tikee_shots (list[ORMTikeeShot]): A list of tikee shots to search through.

    Returns:
        ORMTikeeShot | None: The tikee shot on the opposite side if found; otherwise, None.
    """
    filtered = [
        tikee_shot
        for tikee_shot in tikee_shots
        if TikeeShotSide(tikee_shot.side) == current_side.opposite_side()
    ]
    return filtered[0] if len(filtered) > 0 else None


def is_same_resolution(side_1: ORMTikeeShot, side_2: ORMTikeeShot | None) -> bool:
    """
    Determines whether two ORMTikeeShot objects have the same resolution.

    If side_2 is None, it is assumed that its resolution is the same as side_1.

    Args:
        side_1 (ORMTikeeShot): The primary tikee shot whose resolution is being checked.
        side_2 (ORMTikeeShot | None): The secondary tikee shot to compare, or None.

    Returns:
        bool: True if side_2 is None or if both shots have the same resolution, False otherwise.
    """
    if side_2 is None:
        return True
    return side_1.resolution == side_2.resolution
