#!/bin/bash
# $1 = target url (ex: https://test-url/stage/todo/new )
wrk -t10 -c250 -d5m -swrk.lua $1
