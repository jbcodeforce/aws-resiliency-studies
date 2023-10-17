#!/usr/bin/env python3
import os

import aws_cdk as cdk

from networking.networking_stack import NetworkingStack
from cloud9.cloud9_stack import Cloud9Stack
from backend.backend_stack import BackendStack




app = cdk.App()
ns=NetworkingStack(app, "ResiliencyStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    )
Cloud9Stack(app, 
            "Cloud9Stack", 
            vpc=ns.vpc,
            env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))
            )

BackendStack(app,"BackendStack",
             vpc=ns.vpc,
             cdir=ns.getCIDR(),
             env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))
            )


cdk.Tags.of(app).add("Owner", "Jerome")
app.synth()
