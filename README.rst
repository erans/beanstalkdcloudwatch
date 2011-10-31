beanstalkd_cloudwatch.py - a script to update Beanstalkd stats in AWS CloudWatch
================================================================================

Publish Beanstalkd statistics into AWS CloudWatch as custom metrics.

Usage
=====

Usage: beanstalkd_cloudwatch.py [options]

AWS SQS queue status check command line tool

Options:
  -h, --help            show this help message and exit
  -k AWS_ACCESS_KEY_ID, --aws_access_key_id=AWS_ACCESS_KEY_ID
                        AWS Access Key ID
  -s AWS_SECRET_ACCESS_KEY, --aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                        AWS Secret Access Key
  -H QUEUE_HOST, --queue_host=QUEUE_HOST
                        Beanstalk Host (default: 127.0.0.1)
  -P QUEUE_PORT, --queue_port=QUEUE_PORT
                        Beanstalk port (default: 11300)
  -t TUBE_NAME, --tube_name=TUBE_NAME
                        Name of tube to check. If empty or missing beanstalk
                        global stats will be checked
  -e TUBE_METRIC, --tube_metric=TUBE_METRIC
                        Name of tube (or general metric, if tube_name is not
                        set) metric to check
  -n NAMESPACE, --namespace=NAMESPACE
                        The metric namespace
  -m METRIC_NAME, --metric_name=METRIC_NAME
                        The metric name
  -T TEST_MODE, --test_mode=TEST_MODE
                        Run in test mode
  -l LOG, --log=LOG     Location of the log file
