

import json
import os


def lambda_handler(event, context):
    # Connect to the RDS PostgreSQL database

    # Return response
    return {
        'statusCode': 200,
        'body': "hello world!"
    }
