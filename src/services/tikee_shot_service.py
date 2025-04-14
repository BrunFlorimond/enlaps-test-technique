"""Provide CRUD services for tikee shots object"""

import boto3
import src.constants.constants as constants
import json
from uuid import UUID

from src.model.business.business_modelling import NewTikeeShot, TikeeShotSide
from src.model.orm.orm_modelling import ORMTikeeShot, ORMTikeeShotIdentifier


class TikeeShotServices:
    """Class used to store method for CRUD for tikee shots"""

    def __init__(self):
        """Instanciate a TikeeShotService object storing table in which to write"""
        self.table_name = constants.DDB_TABLE_NAME
        dynamodb = boto3.resource("dynamodb")
        self.tikee_shot_table = dynamodb.Table(constants.DDB_TABLE_NAME)

    def create(self, new_tikee_shot: NewTikeeShot) -> ORMTikeeShot:
        """
        Persist a tikeeshot in DB.
        If a shot already exists with another side, check same resolution
        """

        orm_tikee_shot = new_tikee_shot.to_orm()
        dict_tikee_shot = orm_tikee_shot.model_dump_json(by_alias=True,exclude_none=True,exclude_unset=True)
        self.tikee_shot_table.put_item(Item=json.loads(dict_tikee_shot))
        return orm_tikee_shot

    def get_tikee_shot_by_id(
        self, orm_tikee_shot_identifier: ORMTikeeShotIdentifier
    ) -> ORMTikeeShot | None:
        """Get a tikee shot by Id"""
        response_db = self.tikee_shot_table.get_item(
            Key={"PK": orm_tikee_shot_identifier.PK, "SK": orm_tikee_shot_identifier.SK}
        )
        if "Item" in response_db:
            item = response_db["Item"]
            orm_tikee_shot = ORMTikeeShot(**item)
            return orm_tikee_shot
        else:
            return None

    def get_tikee_shot_of_camera_by_id(self, uuid: UUID) -> list[ORMTikeeShot]:
        """Retrieve all rows of tikee_shot_table with camera uuid"""
        pk = str(uuid)
        response = self.tikee_shot_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Key("PK").begins_with(pk)
        )
        items = response.get("Items", [])
        return [ORMTikeeShot(**item) for item in items]

    def get_tikee_shot_of_sequence(
        self, uuid: UUID, sequence: str
    ) -> list[ORMTikeeShot]:
        pk = self.build_pk(uuid, sequence)
        response = self.tikee_shot_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("PK").eq(pk)
        )
        items = response.get("Items", [])
        return [ORMTikeeShot(**item) for item in items]
    
    def get_tikee_shot_of_photo_index(self, uuid: UUID, sequence: str, photo_index: int | None):
        pk = self.build_pk(uuid, sequence)
        sk = self.build_sk(photo_index, None)
        response = self.tikee_shot_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("PK").eq(pk) & boto3.dynamodb.conditions.Key("SK").begins_with(sk)
        )
        items = response.get("Items", [])
        return [ORMTikeeShot(**item) for item in items]

    def get_tikee_shot(
        self, uuid: UUID, sequence: str, photo_index: int | None, side: TikeeShotSide
    ) -> ORMTikeeShot | None:
        pk = self.build_pk(uuid, sequence)
        sk = self.build_sk(photo_index, side)
        response_db = self.tikee_shot_table.get_item(Key={"PK": pk, "SK": sk})
        if "Item" in response_db:
            item = response_db["Item"]
            return ORMTikeeShot(**item)
        return None

    @staticmethod
    def build_pk(uuid: UUID, sequence: str) -> str:
        return f"{str(uuid)}#{sequence}"

    @staticmethod
    def build_sk(photo_index: int | None, side: TikeeShotSide | None) -> str:
        index = str(photo_index) if photo_index is not None else ""
        photo_side = side.value if side is not None else ""
        return f"{index}#{photo_side}"
