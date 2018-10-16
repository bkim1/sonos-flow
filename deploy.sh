#!/bin/sh
docker build -t flow:latest .
now --public && now alias