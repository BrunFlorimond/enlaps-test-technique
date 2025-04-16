"""File to store constants or load them from OS environment variable"""

import os
import yaml

from pathlib import Path


class IgnoreUnknownTagsLoader(yaml.SafeLoader):
    """Custom loader that ignores unknown YAML tags like !Ref or !GetAtt"""

    def ignore_unknown(self, _):
        """dummy function for constructor"""
        return None  # or you can return node.value if you want to keep the value


IgnoreUnknownTagsLoader.add_constructor(None, IgnoreUnknownTagsLoader.ignore_unknown)

YAML_PATH = Path("cloudformation/dynamodb/dynamodb-setup.yaml")
if not YAML_PATH.exists():
    YAML_PATH = Path("/opt/python") / YAML_PATH
with YAML_PATH.open("r", encoding="utf8") as file:
    dynamodb_setup = yaml.load(file, Loader=IgnoreUnknownTagsLoader)
# DynamoDB
DDB_TABLE_NAME = os.environ.get("DDB_TABLE_NAME")
DDB_ATTRIBUTE = (
    dynamodb_setup.get("Resources", {})
    .get("DDBTable", {})
    .get("Properties", {})
    .get("AttributeDefinitions")
)
DDB_KEYS = (
    dynamodb_setup.get("Resources", {})
    .get("DDBTable", {})
    .get("Properties", {})
    .get("KeySchema")
)
AWS_REGION = os.environ.get("AWS_REGION")
AWS_ACCOUNT_ID = os.environ.get("AWS_ACCOUNT_ID")

LAMBDA_STITCHER = os.environ.get("LAMBDA_STITCHER")
