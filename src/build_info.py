import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class CodeBuildInfo(object):
  def __init__(self, pipeline, buildId):
    self.pipeline = pipeline
    self.buildId = buildId
  
  @staticmethod
  def fromEvent(event):
    logger.info(json.dumps(event, indent=2))
    # strip off leading 'codepipeline/'
    pipeline = event['detail']['additional-information']['initiator'][13:]
    bid = event['detail']['build-id']
    return CodeBuildInfo(pipeline, bid)


class BuildNotification(object):
  def __init__(self, buildInfo):
    self.buildInfo = buildInfo
    

class BuildInfo(object):
  def __init__(self, executionId, pipeline):
    self.executionId = executionId
    self.pipeline = pipeline

  def hasRevisionInfo(self):
    return len(self.revisionInfo) > 0

  @staticmethod
  def pull_phase_info(event):
    info = event['detail']['additional-information']
    return info.get('phases')

  @staticmethod
  def fromEvent(event):
    if event['source'] == "aws.codepipeline":
      detail = event['detail']
      return BuildInfo(detail['execution-id'], detail['pipeline'])
    if event['source'] == "aws.codebuild":
      logger.info(json.dumps(event, indent=2))
      ph = BuildInfo.pull_phase_info(event)
      logger.info(json.dumps(ph, indent=2))

    return None

  @staticmethod
  def fromMessage(event):
    fields = event['attachments'][0]['fields']

    executionId = fields[0]['value']
    status = fields[1]['value']
    pipeline = fields[1]['title']

    return BuildInfo(executionId, pipeline, status)
