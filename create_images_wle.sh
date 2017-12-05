#!/bin/sh
docker build -f wle/Dockerfile_wle-agile-core --tag="jordiescudero/wle-agile-core:1.2.5" wle
docker build -f wle/Dockerfile_wle-agile-zb-protocol --tag="jordiescudero/wle-agile-zb-protocol:1.2.5" wle 
docker build -f wle/Dockerfile_wle-agile-dbus --tag="jordiescudero/wle-agile-dbus:1.2.5" wle
docker build -f wle/Dockerfile_wle-agile-ui --tag="jordiescudero/wle-agile-ui:1.2.5" wle
docker build -f wle/Dockerfile_wle-agile-osjs --tag="jordiescudero/wle-agile-osjs:1.2.5" wle
docker build -f wle/Dockerfile_wle-agile-nodered --tag="jordiescudero/wle-agile-nodered:1.2.5" wle
docker build -f wle/Dockerfile_wle-agile-security --tag="jordiescudero/wle-agile-security:1.2.5" wle

docker push jordiescudero/wle-agile-core:1.2.5
docker push jordiescudero/wle-agile-zb-protocol:1.2.5
docker push jordiescudero/wle-agile-dbus:1.2.5
docker push jordiescudero/wle-agile-ui:1.2.5
docker push jordiescudero/wle-agile-osjs:1.2.5
docker push jordiescudero/wle-agile-nodered:1.2.5
docker push jordiescudero/wle-agile-security:1.2.5


#docker build -f wle/Dockerfile_wle-agile-tento-app --tag="jordiescudero/wle-agile-tento-app:1.2.5" wle
#docker push jordiescudero/wle-agile-tento-app:1.2.5


#docker build -f wle/Dockerfile_wle-homebridge --tag="jordiescudero/wle-homebridge:0.0.1" wle
#docker push jordiescudero/wle-homebridge:0.0.1
