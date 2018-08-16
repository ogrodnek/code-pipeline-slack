# -*- coding: utf-8 -*-

import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from collections import OrderedDict

class MessageBuilder(object):
  def __init__(self, buildInfo, message):
    self.buildInfo = buildInfo
    self.actions = []
    self.messageId = None

    if message:
      logger.info(json.dumps(message, indent=2))
      att = message['attachments'][0]
      self.fields = att['fields']
      self.actions = att.get('actions', [])
      self.messageId = message['ts']
      logger.info("Actions {}".format(self.actions))
    else:
      self.fields = [
        { "title" : buildInfo.pipeline,
          "value" : "UNKNOWN",
          "short" : True
        }
      ]
    
  def hasField(self, name):
    return len([f for f in self.fields if f['title'] == name]) > 0

  def needsRevisionInfo(self):
    return not self.hasField('Revision')

  def attachRevisionInfo(self, rev):
    if self.needsRevisionInfo() and rev:
      if 'revisionUrl' in rev:
        self.fields.append({
          "title": "Revision",
          "value": "<{}|{}: {}>".format(rev['revisionUrl'], rev['revisionId'][:7], rev['revisionSummary']),
          "short": True
        })
      else:
        self.fields.append({
          "title": "Revision",
          "value": rev['revisionSummary'],
          "short": True
        })

  def attachLogs(self, logs):
    self.findOrCreateAction('Build Logs', logs['deep-link'])

  def findOrCreateAction(self, name, link):
    for a in self.actions:
      if a['text'] == name:
        return a
    
    a = { "type": "button", "text": name, "url": link }
    self.actions.append(a)
    return a

  def pipelineStatus(self):
    return self.fields[0]['value']

  def findOrCreatePart(self, title, short=True):
    for a in self.fields:
      if a['title'] == title:
        return a
    
    p = { "title": title, "value": "", "short": short }
    self.fields.append(p)
    return p
  
  def updateBuildStageInfo(self, name, phases, info):
    url = info.get('latestExecution', {}).get('externalExecutionUrl')
    if url:
      self.findOrCreateAction('Build dashboard', url)

    si = self.findOrCreatePart(name, short=False)
    def pi(p):
      p_status = p.get('phase-status', 'IN_PROGRESS')
      return BUILD_PHASES[p_status]
    def fmt_p(p):
      msg = "{} {}".format(pi(p), p['phase-type'])
      d = p.get('duration-in-seconds')
      if d:
        return msg + " ({})".format(d)
      return msg

    def show_p(p):
      d = p.get('duration-in-seconds')
      return p['phase-type'] != 'COMPLETED' and d is None or d > 0

    def pc(p):
      ctx = p.get('phase-context', [])
      if len(ctx) > 0:
        if ctx[0] != ': ':
          return ctx[0]
      return None
    
    context = [pc(p) for p in phases if pc(p)]

    if len(context) > 0:
      self.findOrCreatePart("Build Context", short=False)['value'] = " ".join(context)
    
    pp = [fmt_p(p) for p in phases if show_p(p)]
    si['value'] = " ".join(pp)
  
  def updateStatusInfo(self, stageInfo, stage, status):
    sm = OrderedDict()

    if len(stageInfo) > 0:
      for part in stageInfo.split("\t"):
        (icon, sg) = part.split(" ")
        sm[sg]=icon
    
    icon = STATE_ICONS[status]
    sm[stage] = icon
    
    return "\t".join(['%s %s' % (v, k) for (k, v) in sm.items()])

  def updatePipelineEvent(self, event):
    if event['detail-type'] == "CodePipeline Pipeline Execution State Change":
      self.fields[0]['value'] = event['detail']['state']
    
    if event['detail-type'] == "CodePipeline Stage Execution State Change":
      stage = event['detail']['stage']
      state = event['detail']['state']

      stageInfo = self.findOrCreatePart('Stages')
      stageInfo['value'] = self.updateStatusInfo(stageInfo['value'], stage, state)

  def color(self):
    return STATE_COLORS.get(self.pipelineStatus(), '#eee')

  def message(self):
    return [
      {
        "fields": self.fields,
        "color":  self.color(),
        "footer": self.buildInfo.executionId,
        "actions": self.actions
      }
    ]

# https://docs.aws.amazon.com/codepipeline/latest/userguide/detect-state-changes-cloudwatch-events.html    
STATE_ICONS = {
  'STARTED': ":building_construction:",
  'SUCCEEDED': ":white_check_mark:",
  'RESUMED': "",
  'FAILED': ":x:",
  'CANCELED': ":no_entry:",
  'SUPERSEDED': ""
}

STATE_COLORS = {
  'STARTED': "#9E9E9E",
  'SUCCEEDED': "good",
  'RESUMED': "",
  'FAILED': "danger",
  'CANCELED': "",
  'SUPERSEDED': ""
}

# https://docs.aws.amazon.com/codebuild/latest/APIReference/API_BuildPhase.html
BUILD_PHASES = {
  'SUCCEEDED': ":white_check_mark:",
  'FAILED': ":x:",
  'FAULT': "",
  'TIMED_OUT': ":stop_watch:",
  'IN_PROGRESS': ":building_construction:",
  'STOPPED': ""
}
