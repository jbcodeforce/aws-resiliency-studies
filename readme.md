# AWS Resiliency Studies

This repository includes IaC to prepare environment for HA and resiliency and try to do some chaos engineering. This is for beginner readers.

As illustrated in this diagram, when we want to address Resiliency we need to cover DR and Availability:

![](./docs/diagrams/resiliency.drawio.png)

## CDK stacks

### Networking

The first stack is to define a VPC with 3 AZ, 3 public subnets, 3 private subnets, NAT gateways, routes, and Network load balancer which should match the following diagram:

![](./docs/diagrams/networking-stack.drawio.svg)

To create the stack see the `networking` folder and use cdk CLI.

```sh
cdk synth
cdk deploy
```

Here are the resource created:
* One internet gateway, 3 NAT gateways, one in each in public subnet.
* 3 route tables, one in each public subnet and one in each private subnet
* 3 route tables for the private subnet, that have egress route to NAT
* Security groups
* IAM role for the lambda function to assume, so it can update security groups in VPC
* Lambda function for removing all inbound/outbound rules from the VPC default security group

#### What supports HA in this stack

* 3 AZs with expected routing to authorize ingress traffic on HTTP port 80, and egree via NAT gateways. Any EC2 deployed in the private subnets can fail, a load balancer will route traffic to the one alive.
* With very low latency network between AZs we can do insynch replicas.

#### Disaster recovery

For Availability zone failure, the current topology guaranty services availability. For region recovery, there is nothing in this stack that will help.

### Basic EC2 stack

The second stack is to get some back end systems for testing resiliency. The basic approach is to use an application that returns the AZ.

* The security defines ingress rule for CIDR of the VPC.

## Body of knowledge

* My product agnostic notes on [Disaster Recovery](https://jbcodeforce.github.io/architecture/DR/)
* AWS resiliency [personal notes](https://jbcodeforce.github.io/aws-studies/sa/resiliency/)
