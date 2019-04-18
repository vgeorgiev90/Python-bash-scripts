import json

## Handler format
## entry point for lambda invocations
## script_name.function_name
## In our case
## lambda_function.lambda_handler

def lambda_handler(event, context):
    print(event)
    return {
            'statusCode': 200,
            'body': json.dumps("Simple hello worlds lambda")
    }
