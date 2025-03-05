import boto3
from botocore.exceptions import ClientError

# Configure connection to DynamoDB Local with dummy credentials.
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000",
    region_name="us-east-1",
    aws_access_key_id="dummy",
    aws_secret_access_key="dummy"
)

def create_table_if_not_exists(table_name: str, key_schema: list, attribute_definitions: list):
    try:
        table = dynamodb.Table(table_name)
        table.load()  # This will raise an exception if table doesn't exist.
        return table
    except ClientError as e:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )
        table.wait_until_exists()
        return table

# Create a table for flowcharts. We use "id" as the primary key.
flowchart_table = create_table_if_not_exists(
    "Flowcharts",
    key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
    attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}]
)

# Create a table for nodes.
node_table = create_table_if_not_exists(
    "Nodes",
    key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
    attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}]
)

# Create a table for edges.
edge_table = create_table_if_not_exists(
    "Edges",
    key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
    attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}]
)
