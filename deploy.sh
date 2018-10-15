#!/bin/sh
docker build -t flo:latest .
now --public && now alias