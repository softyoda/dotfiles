#!/usr/bin/env bash
grep -q nvidia-container-runtime /etc/docker/daemon.json && systemctl is-enabled docker.service &>/dev/null && id -nG | grep -qw docker
