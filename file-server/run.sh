#!/bin/bash
mvn spring-boot:run -Drun.jvmArguments="-Xmx1024m -Xms256m -Xgc=parallel" &
