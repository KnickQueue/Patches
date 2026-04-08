# IQ.Pilot PQ Overlay Patch

This overlay contains the IQ.Pilot and VW PQ changes we made in this session.

Included changes:
- Elon Mode toggle fix and monitoring hook
- Konn3kt online timebase fix
- VW live torque self-tune enablement
- PQ flashed-EPS support
- PQ longitudinal feel profiles
- PQ low-speed cornering assist tune
- PQ settings UI cleanup and status panel
- Advanced lane-change tuning controls

Notes:
- The newer build already includes the `onPolicy` model-type support upstream, so that older compatibility patch is intentionally no longer bundled here.

## Refresh The Bundle

Whenever we make new IQ.Pilot changes, refresh the deploy bundle first:

```bash
cd /Users/nicholasquandt/Documents/Dev/Patches/iqpilot/pq_iqpilot_overlay_2026-04-02
./sync_bundle.sh
```

`sync_bundle.sh` uses `FILES.txt` as the source of truth and rebuilds `files/` with the correct mirrored paths.

## Publish The Bundle

To refresh, copy into your local `Patches` checkout, commit, and push in one step:

```bash
cd /Users/nicholasquandt/Documents/Dev/Patches/iqpilot/pq_iqpilot_overlay_2026-04-02
./publish_bundle.sh
```

Optional custom commit message:

```bash
./publish_bundle.sh "Tune PQ low-speed corner assist"
```

## Deploy Over SSH

From the machine that has this patch bundle:

```bash
cd /Users/nicholasquandt/Documents/Dev/Patches/iqpilot/pq_iqpilot_overlay_2026-04-02
./deploy.sh comma@<device-ip> /data/openpilot
```

If your install lives somewhere else on the device, replace `/data/openpilot` with that path.

## What `deploy.sh` does

- refreshes the local bundle from `FILES.txt`
- copies the `files/` overlay to the device
- applies it over the target tree with `rsync`
- runs a quick Python syntax check on the updated Python files

## Manual Deploy

If you prefer to do it by hand:

```bash
./sync_bundle.sh
scp -r files comma@<device-ip>:/tmp/pq_iqpilot_overlay_2026-04-02
ssh comma@<device-ip> 'rsync -a /tmp/pq_iqpilot_overlay_2026-04-02/files/ /data/openpilot/'
```

## On-Device Reapply

If the patch repo is already published to GitHub, the comma can reapply everything itself:

```bash
cd /data/Patches/iqpilot/pq_iqpilot_overlay_2026-04-02
./deploy-device.sh /data/openpilot
```

## Restart

After deploy, restart the UI/process manager or reboot the device so the new params and UI logic are picked up cleanly.
