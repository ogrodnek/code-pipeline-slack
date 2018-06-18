Code Pipeline Slack Bot
=======================

This bot will notify you of CodePipeline progress (using [CloudWatch Events](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/WhatIsCloudWatchEvents.html)).

We attempt to provide a unified summary, by pulling together multiple events, as well as information obtained by the API into a single message view.

![Build](build.gif)


## Launch

| us-east-1 | us-west-2 |
| --------- | --------- |
| [![Launch](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=CodePipelineSlackNotifier&templateURL=https://s3.amazonaws.com/code-pipeline-slack-us-east-1/template.yml) | [![Launch](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=CodePipelineSlackNotifier&templateURL=https://s3-us-west-2.amazonaws.com/code-pipeline-slack-us-west-2/template.yml) |


## Configuration / Customization

No configuration is necessary per pipeline.  As part of the CF Stack, we subscribe to all CodePipeline and CodeBuild events (using [CloudWatch Events](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/WhatIsCloudWatchEvents.html)).

When creating the CloudFormation stack, you can customize:

- `SlackChannel` (defaults to `builds`).
- `SlackBotName` (defaults to `PipelineBuildBot`).
- `SlackBotIcon` (defaults to `:robot_face:` 🤖 ).

Additionally, you must provide `SlackToken`, (see [BotUsers](https://api.slack.com/custom-integrations/bot-users) for creating a slack bot user with an integration token).

## How it works

We utilize [CloudWatch Events](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/WhatIsCloudWatchEvents.html) for CodePipline and CodeBuild to get notified of all status changes.

Using the notifications, as well as using the CodePipeline APIs, we are able to present a unified summary of your Pipeline and Build status.

### IAM permissions

As part of the deployment, we create an IAM policy for the bot lambda function of:

```
Policies:
  - AWSLambdaBasicExecutionRole
  - Version: '2012-10-17'
    Statement:
      - Effect: Allow
        Action:
          - 'codepipeline:Get*'
          - 'codepipeline:List*'
        Resource: '*'
      - Effect: Allow
        Action:
          - 'codebuild:Get*'
        Resource: '*'
```

So we can retrieve information about all pipelines and builds.  See [template.yml](https://github.com/ogrodnek/code-pipeline-slack/blob/master/template.yml) for more detail.
