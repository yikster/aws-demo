#!/usr/bin/env bash

PACKAGE=lambda-phantom-scraper.zip
OUTPUT=dist

aws lambda update-function-code \
--region ap-northeast-2 \
--function-name url2img  \
--zip-file fileb://$PWD/$OUTPUT/$PACKAGE
