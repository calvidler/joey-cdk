from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_rds as rds,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
    aws_apigateway as apigw,
    RemovalPolicy,
    Duration,
    BundlingOptions
)
from constructs import Construct


class DataSize:

    @classmethod
    def bytes(cls, size):
        return size

    @classmethod
    def kilobytes(cls, size):
        return cls.bytes(size) * 1000

    @classmethod
    def megabytes(cls, size):
        return cls.kilobytes(size) * 1000

    @classmethod
    def gigabytes(cls, size):
        return cls.megabytes(size) * 1000

    @classmethod
    def terabytes(cls, size):
        return cls.gigabytes(size) * 1000



class JoeyCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        print(kwargs)
        tags = kwargs['tags']
        self.env = tags['environment']

        

        self.vpc = None

        self.db_security_group = None
        self.lambda_security_group = None

        # The code that defines your stack goes here
        self.lambda_param_max_concurrency=None
        self.lambda_fn= None


        self.database_instance = None

        self.rest_api = None

        
        
        self.sqs_queue = None

        self.create_cdk_resources()


    def create_cdk_resources(self) -> None:
        self.create_vpc()
        self.create_security_groups()
        self.create_database_instance()
        self.create_lambdas()
        self.create_rest_api()

    def create_vpc(self) -> None:
        self.vpc = ec2.Vpc(
            self, 
            f'joey-vpc-{self.env}'
        )

    def create_security_groups(self) -> None:
        self.db_security_group = ec2.SecurityGroup(
            self, 
            f'joey-db-security-group-{self.env}',
            vpc=self.vpc,
            description='Custom Security Group for JoeyDBInstance',
                allow_all_outbound=True
        )

        self.lambda_security_group = ec2.SecurityGroup(
            self, f'JoeyLambdaSecurityGroup-{self.env}',
            vpc=self.vpc,
            description='Security Group for Joey Lambda Function',
            allow_all_outbound=True
        )

        self.db_security_group.add_ingress_rule(
            peer=self.lambda_security_group, 
            connection=ec2.Port.tcp(5432),
            description='Allow Lambda to connect to RDS'
        )


    def create_database_instance(self) -> None:
        self.database_instance = rds.DatabaseInstance(
             self, f'joey-db-instance-{self.env}',
            engine=rds.DatabaseInstanceEngine.postgres(
            version=rds.PostgresEngineVersion.VER_14_8),
            credentials=rds.Credentials.from_generated_secret("joeyAdmin"),
            vpc=self.vpc,
            security_groups=[self.db_security_group], 
            multi_az=False,
            allocated_storage=20,
            removal_policy=RemovalPolicy.DESTROY if self.env == 'develop' else RemovalPolicy.RETAIN,
            delete_automated_backups=True if self.env == 'develop' else False,
            # Retain automated backups for 7 days
            backup_retention=Duration.days(7),
            # publicly_accessible=False,
        )




    def create_lambdas(self) -> None:
        self.lambda_param_max_concurrency = 5
        self.lambda_fn = _lambda.Function(
            self, f'joey-admin-lambda-{self.env}',
            runtime=_lambda.Runtime.PYTHON_3_8,
            timeout=Duration.seconds(15),

            security_groups=[self.lambda_security_group],
            handler='app.lambda_handler',
            vpc=self.vpc,  # Ensure your Lambda function is associated with the VPC
            code=_lambda.Code.from_asset(
                './joey_lambda',
        
            ),
               environment={
                "Test": "Test",
            },
            # environment=db_creds
        )

    def create_rest_api(self) -> None:
        self.rest_api = apigw.LambdaRestApi(
            self, f'joey-rest-api-gateway-{self.env}',
            handler=self.lambda_fn,
             deploy_options=apigw.StageOptions(
                stage_name=f'joey-api-{self.env}',
            ),
        )

        # Sample endpoint
        get_endpoint = self.rest_api.root.add_resource('sample')
        get_endpoint.add_method('GET')

    
