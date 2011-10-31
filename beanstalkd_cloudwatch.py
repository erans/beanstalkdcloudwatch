#!/usr/bin/python
#
# Copyright 2009 Eran Sandler (eran@sandler.co.il)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys
import logging
import logging.handlers
from optparse import OptionParser

from boto.ec2.cloudwatch import CloudWatchConnection
from boto.sns import SNSConnection

import beanstalkc

class BeanstalkCloudWatch(object):
	_cloud_watch_connection = None
	
	def __init__(self, aws_access_key, aws_secret_access_key, queue_host, queue_port, tube_name, tube_metric, namespace, metric_name, test_mode):
		if aws_access_key is None or aws_access_key == "":
			raise Exception("aws_access_key cannot be null")
			
		if aws_secret_access_key is None or aws_secret_access_key == "":
			raise Exception("aws_secret_access_key cannot be null")
		
		if queue_host is None or queue_host == "":
			raise Exception("queue_host cannot be null")

		if queue_port is None or queue_port == "":
			raise Exception("queue_port cannot be null")
		
		if tube_metric is None or tube_metric == "":
			raise Exception("tube_metric cannot be null")
		
		if namespace is None or namespace == "":
			raise Exception("namespace cannot be null")
		
		if metric_name is None or metric_name == "":
			raise Exception("metric_name cannot be null")
		
		self.aws_access_key = aws_access_key
		self.aws_secret_access_key = aws_secret_access_key
		
		self.queue_host = queue_host
		self.queue_port = int(queue_port)
		self.tube_name = tube_name
		self.tube_metric = tube_metric
		self.namespace = namespace
		self.metric_name = metric_name
		
		self.test_mode = test_mode == "1"
			
	@property
	def cloud_watch_connection(self):
		if self._cloud_watch_connection is None:
			self._cloud_watch_connection = CloudWatchConnection(self.aws_access_key, self.aws_secret_access_key)
		
		return self._cloud_watch_connection
			
	def check(self):
		logging.info("Check Started")
		
		connection = beanstalkc.Connection(self.queue_host, self.queue_port)
		
		if self.tube_name and self.tube_name != "":
			logging.info("Reading stats from tube '%s'" % self.tube_name)
			stats = connection.stats_tube(self.tube_name)			
		else:
			logging.info("Reading server stats")			
			stats = connection.stats()			
		
		count = None	
		if self.tube_metric in stats:
			logging.info("Reading tube metric '%s'" % self.tube_metric)
			count = stats[self.tube_metric]
		else:
			raise Exception("%s cannot be found in the stats. Please check the metric name." % self.tube_metric)
		
		logging.info("%s value: %s" % (self.tube_metric, count))
		
		if not self.test_mode:
			result = self.cloud_watch_connection.put_metric_data(self.namespace, self.metric_name, count, unit="Count")
			logging.info("Call Result: %s" % str(result))
		else:
			print "%s value: %s   Setting to namespace=%s metric_name=%s" % (self.metric_name, count, self.namespace, self.metric_name)
		logging.info("Check Ended")

def main():	
	parser = OptionParser(description='AWS SQS queue status check command line tool')
	parser.add_option('-k', '--aws_access_key_id', help='AWS Access Key ID')
	parser.add_option('-s', '--aws_secret_access_key', help='AWS Secret Access Key')
	parser.add_option("-H", "--queue_host", help="Beanstalk Host (default: 127.0.0.1)", default="127.0.0.1")
	parser.add_option("-P", "--queue_port", help="Beanstalk port (default: 11300)", default="11300")
	parser.add_option('-t', '--tube_name', help='Name of tube to check. If empty or missing beanstalk global stats will be checked', default=None)
	parser.add_option('-e', '--tube_metric', help='Name of tube (or general metric, if tube_name is not set) metric to check')
	parser.add_option('-n', '--namespace', help='The metric namespace')
	parser.add_option('-m', '--metric_name', help='The metric name')
	parser.add_option('-T', '--test_mode', help="Run in test mode", default="0")
	parser.add_option('-l', '--log', help="Location of the log file")

	(options, args) = parser.parse_args()
	
	if options.aws_access_key_id is None and options.aws_secret_access_key is None:
		env_AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
		env_AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
		if not (env_AWS_ACCESS_KEY_ID and env_AWS_SECRET_ACCESS_KEY):
			print "ERROR: Missing AWS_ACCESS_KEY_ID parameter. Set it via command line or via the AWS_ACCESS_KEY_ID envrionment variable."
			print "ERROR: Missing AWS_SECRET_ACCESS_KEY parameter. Set it via command line or via the AWS_SECRET_ACCESS_KEY envrionment variable."
			sys.exit(2)
		else:
			options.aws_access_key_id = env_AWS_ACCESS_KEY_ID
			options.aws_secret_access_key = env_AWS_SECRET_ACCESS_KEY
	
	if options.log:
		logger = logging.getLogger()
		handler = logging.handlers.TimedRotatingFileHandler(options.log, "midnight", backupCount=3, utc=True)
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		logger.setLevel(logging.INFO)
		
	watch_queue_count = BeanstalkCloudWatch(options.aws_access_key_id, options.aws_secret_access_key, options.queue_host, options.queue_port, options.tube_name, 
		options.tube_metric, options.namespace, options.metric_name, options.test_mode)
	watch_queue_count.check()

if __name__ == "__main__":
	main()