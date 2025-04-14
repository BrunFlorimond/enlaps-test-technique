"""Provide Mock AWS ressources for tests"""

import boto3
import pytest
import src.constants.constants as constants


@pytest.fixture()
def tikee_shot_table():

    class MockedDDBConstructor:
        """Create a mock DynamoDB resource"""

        def create_tikee_shot_table(self):
            """Create a tikee_shot table"""
            dynamodb = boto3.resource("dynamodb")

            key_schema = constants.DDB_KEYS
            attribute_definitions = constants.DDB_ATTRIBUTE
            table_name = constants.DDB_TABLE_NAME

            # Create the table in the mocked DynamoDB
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                BillingMode="PAY_PER_REQUEST",
            )
            # Wait for the table to be created (important for testing)
            table.meta.client.get_waiter("table_exists").wait(TableName=table_name)

            return table

    return MockedDDBConstructor()
