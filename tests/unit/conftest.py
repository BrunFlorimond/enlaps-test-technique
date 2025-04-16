"""Provide Mock AWS ressources for tests"""

import boto3
import pytest
import src.constants.constants as constants

import json


@pytest.fixture()
def tikee_shot_table():

    class MockedDDBConstructor:
        """Create a mock DynamoDB resource"""

        def create_tikee_shot_table(self):
            """Create a tikee_shot table"""
            dynamodb = boto3.resource("dynamodb", constants.AWS_REGION)

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

@pytest.fixture()
def stitcher_lambda():

    class MockedLambdaStitcherConstructor:
        """Create a mocked lambda stitcher"""

        def create_stitcher_lambda(self):
            """Create mocked Lambda"""
            iam_client = boto3.client('iam', constants.AWS_REGION)

            assume_role_policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }

            role_response = iam_client.create_role(
                RoleName='lambda-test-role',
                AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
            )

            # Create mock lambda
            lambda_client = boto3.client('lambda', constants.AWS_REGION)
            lambda_client.create_function(
                FunctionName=constants.LAMBDA_STITCHER,
                Runtime='python3.13',
                Role=f"arn:aws:iam::123456789012:role/lambda-test-role",
                Handler='lambda_create_stich.lambda_handler',
                Code={'ZipFile': b'dummy code'},
            )

            return lambda_client, iam_client
    return MockedLambdaStitcherConstructor()

