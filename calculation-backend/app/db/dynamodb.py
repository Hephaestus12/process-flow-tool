import boto3

TABLE_NAME = "Flowcharts"

# Connect to local DynamoDB
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000",
    region_name="us-east-1"
)

try:
    table = dynamodb.Table(TABLE_NAME)
    table.load()  # Ensure the table exists
except Exception as e:
    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "name", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "name", "AttributeType": "S"}
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }
    )
    table.wait_until_exists()
