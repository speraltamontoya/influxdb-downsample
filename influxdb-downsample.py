#!/usr/bin/python
"""
apt-get install python-influxdb
	or
pip install influxdb
pip install --upgrade influxdb
"""

import argparse
from influxdb import InfluxDBClient

def checkCq(client,database,retentionPolicy,measurement):
	cqs = client.query("show continuous queries")
	if list(cqs.get_points(tags={"name": database + "_" + retentionPolicy + "_" + measurement})):
		""" Continuous query exists """
		return True
	else:
		""" Continuous query not exists """
		return False

""" def chargeData(client,database,retentionPolicy,measurement,groupTime,line): """

def getMeasurements(client):
	m = client.query("show measurements")
	return list(map(lambda x: x["name"],m.get_points()))

def getFields(client,measurement):
	fields = client.query('show field keys from \"' + measurement + "\"")
	return fields

def countFields(fields):
	nfield=0
	for field in fields:
		nfield += 1
	return nfield

def main(host='localhost', port=8086, database='', user='', password='', rtSource='autogen', retentionPolicy='history', groupTime='1h', duration='INF'):
	""" Instantiate a connection to the InfluxDB. """
	client = InfluxDBClient(host, port, user, password, database,timeout=None)
	
	if not list(client.query("show retention policies").get_points(tags={"name": retentionPolicy })):
		client.create_retention_policy(retentionPolicy, duration, 1, database, default=False, shard_duration=u'1d')
	
	measurements = getMeasurements(client)	
	for measurement in measurements:
		if not checkCq(client,database,retentionPolicy,measurement):
			fields = getFields(client,measurement)
			nfields = countFields(fields.get_points())
			
			line = ""
			for field in fields.get_points():
				if field["fieldType"] == "string":
					line = line + "first(\"" + field["fieldKey"] + "\") as \"" + field["fieldKey"] + "\","
				else:
					if nfields <= 15:
						line = line + "mean(\"" + field["fieldKey"] + "\") as \"" + field["fieldKey"] + "\","
					else:
						line = line + "mean(\"" + field["fieldKey"] + "\") as \"" + field["fieldKey"] + "\","
						line = line + "max(\"" + field["fieldKey"] + "\") as \"" + field["fieldKey"] + "_max\","

			CQNAME = database + "_" + retentionPolicy + "_" + measurement
			FROM = database + "." + rtSource + "." + measurement
			INTO = database + "." + retentionPolicy + "." + measurement
			
			Query = "SELECT " + line[:-1] + " INTO " + INTO + " FROM " + FROM + " WHERE time < now()-" + groupTime + " GROUP BY time(" + groupTime + "),*"
			QueryCQ = "CREATE CONTINUOUS QUERY " + CQNAME + " ON " + database + " BEGIN " + Query + " END "
			client.query(Query)
			client.query(QueryCQ)

def parse_args():
	"""Parse the args."""
	parser = argparse.ArgumentParser(description='example code to play with InfluxDB')
	parser.add_argument('--host', type=str, required=False, default='localhost', help='hostname of InfluxDB http API')
	parser.add_argument('--port', type=int, required=False, default=8086, help='port of InfluxDB http API')
	parser.add_argument('--database', type=str, required=False, default='telegraf', help='database of InfluxDB http API')
	parser.add_argument('--user', type=str, required=False, default='', help='user of InfluxDB http API')
	parser.add_argument('--password', type=str, required=False, default='', help='password of InfluxDB http API')
	parser.add_argument('--rtSource', type=str, required=False, default='autogen', help='default: history')
	parser.add_argument('--retentionPolicy', type=str, required=False, default='history', help='default: history')
	parser.add_argument('--groupTime', type=str, required=False, default='1h', help='default: 1h | examples: 15m, 30m, 1h...')
	parser.add_argument('--duration', type=str, required=False, default='INF', help='default: INF | duration - the duration of the new retention policy.')
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_args()
	main(host=args.host, port=args.port, database=args.database, user=args.user, password=args.password, rtSource=args.rtSource, retentionPolicy=args.retentionPolicy, groupTime=args.groupTime, duration=args.duration)
