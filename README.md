# Introduction
This project deals with data acquisition, GUI, decision making.
Fileds: smart home, IoT, SCADA, dispatching and monitoring systems.
# First step
1. [Victoriametrics](https://victoriametrics.com/) as time-series database (TSDB).
2. [Grafana](https://grafana.com/) as GUI.
# Second step
Peresvet: own decision as infrastructure system.
Base functionality:
1. Use Victoriametrics as TSDB.
2. Create tags (crud commands). One tag - one metric.
3. Read/write data.
4. Use LDAP server for entity descriptions.
# Third step
Typical connector for ESP32 controller.
Will write data to Peresvet over http requests and will realize some control algorithm.
# Next steps
Functional evolution.
Peresvet:
1. Use different background storages as TSDB.
2. Make object hierarchy. Every object may have tag set.
   This hierarchy is build on LDAP server
3. Use websockets
4. RabbitMQ
5. Not only read data over connector, but write it also. User can control devices over WebUI.

