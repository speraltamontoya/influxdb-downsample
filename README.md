# influxdb-downsample
It is a python script for the automatic creation of retention policies and continuous queries.

This script uses the InfluxDB-Python library. https://github.com/influxdata/influxdb-python

# Parameters

```
--host
--port
--database
--user
--password
--rtSource         | name of retention policy source of data. default: "autogen"
--retentionPolicy  | name of the retention policy to create. default: "history"
--groupTime        | time groupings for samples. default: "1h"
--duration         | expiration time of the retention policy. default: "INF"
```

# Usage examples
```
python influxdb-downsample.py --database telegraf
```

```
python influxdb-downsample.py --user *** --password *** --database telegraf
```

```
python influxdb-downsample.py --user *** --password *** --database telegraf --retentionPolicy 40minutes --groupTime 20m --duration '40d'
```

