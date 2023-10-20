from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    CfnOutput,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct

with open("./backend/user_data/user_data.sh") as f:
    user_data = f.read()

key_name = "my-ec2-key-pair"
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
        asg=autoscaling.AutoScalingGroup(self, "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            machine_image=amzn_linux,
            key_name=key_name,
            security_group=self.ec2_security_group,
            user_data=ec2.UserData.custom(user_data),
            min_capacity=1,
            max_capacity=2,
            desired_capacity=2,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            # availability_zones=["us-west-2a", "us-west-2b"]
        )

        lb = elbv2.ApplicationLoadBalancer(self, "ALB",
                vpc=vpc,
                internet_facing=True
            )
        listener = lb.add_listener("Listener",
                    port=80,
                    open=True
                    )

        # Create an AutoScaling group and add it as a load balancing
        # target to the listener.
        listener.add_targets("ApplicationFleet",
            port=80,
            targets=[asg]
        )