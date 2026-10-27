#!/usr/bin/env bash
[[ $(kreadconfig6 --file powerdevilrc --group AC --group SuspendAndShutdown --key PowerButtonAction) == 8 ]]
