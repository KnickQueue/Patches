#!/usr/bin/bash

# 1. Ensure parameters are writable
mkdir -p /data/params/d

# Initialize Elon Mode parameters with ON by default
if [ ! -f /data/params/d/ElonMode ]; then
  echo -n "1" > /data/params/d/ElonMode
fi
if [ ! -f /data/params/d/ShowDmDebug ]; then
  echo -n "0" > /data/params/d/ShowDmDebug
fi

# 3. Finalize and Reboot
echo "Elon Mode and PQ Optimizations setup complete."
