#!/bin/bash

module_name=$1

echo sudo puppet module install ${module_name}

sudo puppet module install ${module_name}

exit