#!/usr/bin/bash

# Elon Mode & DM Debug Setup (System Config & Persistence)
# This script handles roaming, unmetered data, and persistence.
# It assumes the code changes have been pulled via git.

set -e

NON_INTERACTIVE=false
if [ "$1" == "--non-interactive" ]; then
    NON_INTERACTIVE=true
fi

echo "--- Elon Mode & DM Debug Setup ---"

# 1. Enable Roaming & Unmetered Data
echo "Configuring system settings..."
settings put global data_roaming 1
settings put global tether_dun_required 0

# Set Cellular Data to Unmetered
ACTIVE_CON=$(nmcli -t -f uuid,type connection show --active | grep gsm | cut -d: -f1 || true)
if [ -n "$ACTIVE_CON" ]; then
    nmcli connection modify "$ACTIVE_CON" connection.metered no
    echo "Cellular connection ($ACTIVE_CON) set to unmetered."
fi
echo "System settings configured."

# 2. Persistence
if [ "$NON_INTERACTIVE" = false ]; then
    echo "Setting up persistence..."
    # Ensure this script is in /data/openpilot/ for the hook
    if [ ! -f "/data/openpilot/setup_elon_mode.sh" ]; then
        cp "$0" /data/openpilot/setup_elon_mode.sh
        chmod +x /data/openpilot/setup_elon_mode.sh
    fi

    # Add to launch_openpilot.sh if present
    if [ -f "launch_openpilot.sh" ]; then
        if ! grep -q "setup_elon_mode.sh" launch_openpilot.sh; then
            # Insert after hashbang
            sed -i '2i bash /data/openpilot/setup_elon_mode.sh --non-interactive' launch_openpilot.sh
            echo "Persistence added to launch_openpilot.sh."
        fi
    fi
fi

echo "--- Setup Complete! ---"
if [ "$NON_INTERACTIVE" = false ]; then
    echo "Rebooting or restarting the UI may be required for all settings to apply."
fi
