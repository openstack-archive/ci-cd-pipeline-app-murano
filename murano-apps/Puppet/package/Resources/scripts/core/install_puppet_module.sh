#!/bin/bash

module_name=$1

sudo puppet module install ${module_name}

exit
