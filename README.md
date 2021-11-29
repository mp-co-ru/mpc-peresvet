# Introduction
This project deals with data acquisition, GUI, decision making.
Fileds: smart home, IoT, SCADA, dispatching and monitoring systems.
# How to use
Open documentation (index.html) and read Concept for current functionality and Installation for Peresvet installation procedure.
# Development
Approximate stages of development are described here.
# Debug
So, this chapter deals with VS Code.
Thanks to https://github.com/Kludex/fastapi-docker-debug:
1. Run: ```$ docker-compose -f docker-compose.yml -f docker-compose.debug.yml up```
2. Press `F5` in VS Code...
3. You may debug code!

## First step
1. [Victoriametrics](https://victoriametrics.com/) as time-series database (TSDB).
2. [Grafana](https://grafana.com/) as GUI.
3. Short python script to write data to one metric.
## Second step
Peresvet: own decision as infrastructure system.
Base functionality:
1. Use Victoriametrics as TSDB.
2. Create tags (crud commands). One tag - one metric.
3. Read/write data.
4. Use LDAP server for entity descriptions.
## Third step
Typical connector for ESP32 controller.
Will write data to Peresvet over http requests and will realize some control algorithm.
## Next steps
Functional evolution.
Peresvet:
1. Use different background storages as TSDB.
2. Make object hierarchy. Every object may have tag set.
   This hierarchy is build on LDAP server
3. Use websockets
4. Not only read data over connector, but write it also. User can control devices over WebUI.
5. Calculated tags
6. External method calls
7. Alerts
8. RabbitMQ

