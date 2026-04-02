# IQ.Pilot PQ Overlay Patch

This overlay contains the IQ.Pilot and VW PQ changes we made in this session.

Included changes:
- Elon Mode toggle fix and monitoring hook
- Konn3kt online timebase fix
- VW live torque self-tune enablement
- PQ flashed-EPS support
- PQ longitudinal feel profiles
- PQ settings UI cleanup and status panel
- Advanced lane-change tuning controls

## Deploy Over SSH

From any machine that can reach the device:

```bash
git clone --single-branch --branch codex/pq-iqpilot-overlay-2026-04-02 https://github.com/KnickQueue/Patches.git
cd Patches/iqpilot/pq_iqpilot_overlay_2026-04-02
./deploy.sh comma@<device-ip> /data/openpilot
```

If your install lives somewhere else on the device, replace `/data/openpilot` with that path.

## What `deploy.sh` does

- copies the `files/` overlay to the device
- applies it over the target tree with `rsync --relative`
- runs a quick Python syntax check on the updated Python files

## Restart

After deploy, restart the UI/process manager or reboot the device so the new params and UI logic are picked up cleanly.
