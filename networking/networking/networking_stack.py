from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct
import boto3


vpc_name="ResiliencyVpc"
cidr_mask=24
CIDR="10.0.0.0/16"

'''
Create VPC with 3 AZs, 3 public subnets and 3 private subnets.
One internet gateway, 3 NAT gateways, one in each in public subnet.
3 route tables, one in each public subnet and one in each private subnet
3 route tables for the private subnet, that have egress route to NAT
Security groups
IAM role to update security group in VPC
Lambda function for removing all inbound/outbound rules from the VPC default security group
'''
class NetworkingStack(Stack):
   
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
       
        self.vpc = self.lookup_vpc(vpc_name)
        if self.vpc == None:
            self.vpc=self.create_vpc(vpc_name)
        self.add_security_groups(self.vpc)
        CfnOutput(self,"VPC", value=self.vpc.vpc_id, export_name="vpc")

    
    def lookup_vpc(self, vpc_name: str) -> ec2.Vpc:
        client = boto3.client('ec2')
        response = client.describe_vpcs(
                        Filters=[{
                            'Name': 'tag:Name',
                            'Values': [
                                vpc_name
                            ]
                        }]
                    )
        if len(response['Vpcs']) > 0:
            vpc=response['Vpcs'][0]
        else:
            vpc= None
        return vpc
    
    def create_vpc(self, vpc_name: str) -> ec2.Vpc:
        vpc = ec2.Vpc(self, vpc_name,
            max_azs=3,
            vpc_name=vpc_name,
            nat_gateways=3,
            ip_addresses=ec2.IpAddresses.cidr(CIDR),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=cidr_mask
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=cidr_mask
                )
            ]
        )
        return vpc
    
    def add_security_groups(self, vpc: ec2.Vpc) -> None:
        print("add security groups")

    def getCIDR(self) -> str:
        return CIDR
