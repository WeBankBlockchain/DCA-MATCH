#!/bin/bash

ps -ef|grep matcher_ | grep -v grep|awk '{print $2}'|xargs kill -9

