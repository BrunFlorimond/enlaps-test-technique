"""Lambda to create product in dynamo DB table"""
import os
import json
import logging
import boto3

from pydantic import ValidationError

from src.model.base.base_modelling import TikeeShotSide
from src.model.business.business_modelling import NewTikeeShot
from src.model.orm.orm_modelling import ORMTikeeShot
from src.services.tikee_shot_service import TikeeShotServices
from src.constants.constants import LAMBDA_STITCHER, AWS_REGION, AWS_ACCOUNT_ID


logger = logging.getLogger()
logger.setLevel(logging.INFO)



lambda_client = boto3.client('lambda')


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
        other_side = get_photo_with_side(
                TikeeShotSide(new_tikee_shot.side).opposite_side(), photos_with_same_index
            )
        if is_same_resolution(
            new_tikee_shot.to_orm(),
            other_side,
        ):
            orm_tikee_shot = tikee_shot_service.create(new_tikee_shot)
            if other_side is not None:
                photos_with_same_index.append(orm_tikee_shot)
                left_side: ORMTikeeShot | None = get_photo_with_side(TikeeShotSide.LEFT, photos_with_same_index)
                right_side: ORMTikeeShot | None = get_photo_with_side(TikeeShotSide.RIGHT, photos_with_same_index)
                if left_side is not None and right_side is not None:
                    input = json.dumps({"body":
                        {
                            "left_side_s3_path": left_side.build_s3_path(),
                            "right_side_s3_path": right_side.build_s3_path()
                        }})
                    lambda_client.invoke(
                        FunctionName=f"arn:aws:lambda:{AWS_REGION}:{int(AWS_ACCOUNT_ID)}:function:{LAMBDA_STITCHER}",
                        InvocationType='Event',
                        Payload=input
                    )
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


def get_photo_with_side(side: TikeeShotSide, tikee_shots: list[ORMTikeeShot]) -> ORMTikeeShot | None:
    """
    Return the first tikee shot from the provided list that matches the specified side.

    This function iterates through the supplied list of tikee shots and returns the first shot
    whose side equals the provided side. If no such shot is found, it returns None.

    Args:
        side (TikeeShotSide): The side to filter the tikee shots by.
        tikee_shots (list[ORMTikeeShot]): A list of tikee shots to search through.

    Returns:
        ORMTikeeShot | None: The first tikee shot matching the specified side, or None if no match exists.
    """
    filtered = [
        tikee_shot
        for tikee_shot in tikee_shots
        if TikeeShotSide(tikee_shot.side) == side
    ]
    return filtered[0] if filtered else None


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
