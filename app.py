#!/usr/bin/env python3
import os
import aws_cdk as cdk
from joey_cdk.joey_cdk_stack import JoeyCdkStack
import git


def get_context(app: cdk.App) -> dict:
    git_branch = git.Repo(os.getcwd()).active_branch.name
    print(f'Using git branch: {git_branch}')
    print(app.node.try_get_context('defaultEnvironment'))
    if app.node.try_get_context('environments') is None:
        environment = git_branch
    else:
        environment = next((e for e in app.node.try_get_context(
            'environments') if e['branchName'] == git_branch), None)
    if environment is None:
        raise Exception(f'No environment found for branch {git_branch}')
    globals = app.node.try_get_context('globals')
    return {**globals, **environment}



def create_joey_stack():
    app = cdk.App()

    context = get_context(app)
    tags = {
        "environment": context['environment'],
    }
    app_id = f"JoeyCdkStack-{tags['environment']}"

    JoeyCdkStack(
        app, 
        app_id,
        env=cdk.Environment(
            account=context['accountNumber'], 
            region=context['region']),
        tags=tags,
    )

    app.synth()

create_joey_stack()