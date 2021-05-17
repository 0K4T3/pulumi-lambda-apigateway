import os

import pulumi
import pulumi_aws as aws


ENV = os.getenv('ENV', 'local')
LOCALSTACK_ENDPOINT = 'http://localhost:4566'


localstack_provider = aws.Provider(
    'localstack',
    access_key='dummy',
    secret_key='dummy',
    region='us-east-1',
    skip_credentials_validation=False,
    skip_metadata_api_check=False,
    skip_region_validation=False,
    skip_requesting_account_id=False,
    endpoints=[{
        'apigateway': LOCALSTACK_ENDPOINT,
        'dynamodb': LOCALSTACK_ENDPOINT,
        'lambda': LOCALSTACK_ENDPOINT,
    }],
)


lambda_function_name = f'{ENV}Function'
function = aws.lambda_.Function(
    lambda_function_name,
    name=lambda_function_name,
    role='',
    runtime='python3.8',
    handler='app.lambda_handler',
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive('./app_code'),
    }),
)


rest_api_name = f'{ENV}API'
rest_api = aws.apigateway.RestApi(
    rest_api_name,
    name=rest_api_name,
    opts=pulumi.ResourceOptions(provider=localstack_provider),
)


api_resource_name = f'{ENV}Resource'
api_resource = aws.apigateway.Resource(
    api_resource_name,
    rest_api=rest_api.id,
    parent_id=rest_api.root_resource_id,
    path_part='/{proxy+}',
    opts=pulumi.ResourceOptions(provider=localstack_provider),
)


api_medthod_name = f'{ENV}Method'
api_method = aws.apigateway.Method(
    api_method_name,
    authorization='NONE',
    http_method='ANY',
    rest_api=rest_api.id,
    resource_id=api_resource.id,
    opts=pulumi.ResourceOptions(provider=localstack_provider),
)


api_integration_name = f'{ENV}Integration'
api_integration = aws.apigateway.Integration(
    rest_api=rest_api.id,
    resource_id=api_resource.id,
    http_method=api_method.http_method,
    type='AWS_PROXY',
    opts=pulumi.ResourceOptions(provider=localstack_provider),
)


api_deployment_name = f'{ENV}deployment'
api_deployment = aws.apigateway.Deployment(
    api_deployment_name,
    rest_api=rest_api.id,
    stage_name='api',
    opts=pulumi.ResourceOptions(provider=localstack_provider),
)
