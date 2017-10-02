#!/bin/sh
docker build -f wle/Dockerfile_wle-agile-core --tag="jordiescudero/wle-agile-core:1.0.0" wle
docker build -f wle/Dockerfile_wle-agile-zb-protocol --tag="jordiescudero/wle-agile-zb-protocol:1.0.0" wle 
docker build -f wle/Dockerfile_wle-agile-tento-app --tag="jordiescudero/wle-agile-tento-app:1.0.0" wle
docker build -f wle/Dockerfile_wle-agile-dbus --tag="jordiescudero/wle-agile-dbus:1.0.0" wle
docker build -f wle/Dockerfile_wle-agile-ui --tag="jordiescudero/wle-agile-ui:1.0.0" wle
docker build -f wle/Dockerfile_wle-agile-osjs --tag="jordiescudero/wle-agile-osjs:1.0.0" wle
docker build -f wle/Dockerfile_wle-agile-nodered --tag="jordiescudero/wle-agile-nodered:1.0.0" wle
docker build -f wle/Dockerfile_wle-agile-security --tag="jordiescudero/wle-agile-security:1.0.0" wle

#docker push jordiescudero/wle-agile-core:1.0.0
#docker push jordiescudero/wle-agile-zb-protocol:1.0.0
#docker push jordiescudero/wle-agile-tento-app:1.0.0
#docker push jordiescudero/wle-agile-dbus:1.0.0
#docker push jordiescudero/wle-agile-ui:1.0.0
#docker push jordiescudero/wle-agile-osjs:1.0.0
#docker push jordiescudero/wle-agile-nodered:1.0.0
#docker push jordiescudero/wle-agile-security:1.0.0