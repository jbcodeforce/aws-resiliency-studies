from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct

with open("./backend/user_data/user_data.sh") as f:
    user_data = f.read()

key_name = "my-key-pair"
amzn_linux = ec2.MachineImage.latest_amazon_linux2(
    edition=ec2.AmazonLinuxEdition.STANDARD,
    virtualization=ec2.AmazonLinuxVirt.HVM,
    storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
)

'''
To simulate cell architecture with stack within the same AZ we want one ALB per AZ, an auto scaling group per
AZ and at least one EC2 per ASG.  
'''
class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, cdir: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.ec2_security_group = ec2.SecurityGroup(self, "EC2privateSG",
                                                  vpc=vpc,
                                                  description="SecurityGroup for EC2 in private subnet",
                                                  security_group_name="EC2privateSG",
                                                  allow_all_outbound=True,
                                                  )

        self.ec2_security_group.add_ingress_rule(ec2.Peer.ipv4(cdir), ec2.Port.tcp(22), "allow ssh access from the VPC")
        self.ec2_security_group.add_ingress_rule(ec2.Peer.ipv4(cdir), ec2.Port.tcp(80), "allow HTTP access from the VPC")

        self.instance = ec2.Instance(self, "myHttpdEC2",
                                     instance_type=ec2.InstanceType("t2.micro"),
                                     instance_name="mySimpleHTTPserver",
                                     machine_image=amzn_linux,
                                     vpc=vpc,
                                     key_name=key_name,
                                     vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                                     security_group=self.ec2_security_group,
                                     user_data=ec2.UserData.custom(user_data),
                                     )