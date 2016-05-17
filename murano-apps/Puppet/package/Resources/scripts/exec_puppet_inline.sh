#!/usr/bin/env bash

PUPPET_CODE=$1

puppet apply --execute "${PUPPET_CODE}"