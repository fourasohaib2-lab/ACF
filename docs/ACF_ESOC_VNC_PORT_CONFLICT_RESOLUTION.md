# PROCEDURAL GUIDE: RESOLVING QT VNC PORT CONFLICT ON HPC (ACF ESOC)

**Host HPC:** `sms1` (`10.16.20.2`)  
**User:** `sfoura`  
**Workspace:** `/onm/dem/home/sfoura/ACF`  
**Error:** `QVncServer could not connect: "The bound address is already in use"`  

---

## 1. ROOT CAUSE ANALYSIS

When Qt VNC platform (`QT_QPA_PLATFORM="vnc:size=1920x1080:port=5900"`) is launched, `QVncServer` attempts to bind to TCP port `5900`.

If port `5900` is already bound by:
1. An orphaned or background `python -m acf.gui.app` process from a previous SSH session.
2. A system VNC server (e.g. `vino`, `x11vnc`, `vino-server`, `xrdp`).
3. Another HPC user running a VNC server on the shared login node `sms1`.

Qt raises `QVncServer could not connect: "The bound address is already in use"` and exits.

---

## 2. ORDERED RESOLUTION COMMANDS (EXECUTE ON `sms1`)

### STEP 1: Identify Process Using Port 5900

```bash
# Check socket ownership on port 5900
ss -tulpn | grep 5900

# Alternatively, use lsof or fuser
lsof -i :5900
```

### STEP 2: Find Old/Orphaned ACF Python GUI Processes

```bash
# Search for active python GUI sessions
ps aux | grep "acf.gui.app" | grep -v grep
```

### STEP 3: Terminate Orphaned Processes

```bash
# Kill orphaned acf.gui.app processes belonging to user sfoura
pkill -f "acf.gui.app"

# If process persists, force kill
kill -9 $(pgrep -f "acf.gui.app")
```

### STEP 4: Verify Port 5900 is Free

```bash
# Confirm port 5900 is no longer listening
ss -tulpn | grep 5900
```

---

## 3. DYNAMIC PORT SELECTION (PERMANENT HPC SOLUTION)

To avoid conflicts on shared HPC login nodes, assign a dynamic port based on the user's UID (e.g., `5900 + (UID % 100)` or port `5910`):

```bash
# Set environment
conda activate acf-hpc
export PYTHONPATH=/onm/dem/home/sfoura/ACF/src:$PYTHONPATH

# Use dynamic/unallocated port (e.g., port 5910)
export QT_QPA_PLATFORM="vnc:size=1920x1080:port=5910"

# Launch ACF ESOC
python -m acf.gui.app
```

---

## 4. SSH TUNNEL & CLIENT CONNECTION FROM UBUNTU PC

From your local Ubuntu terminal:

```bash
# Tunnel local port 5910 to sms1 port 5910
ssh -N -L 5910:localhost:5910 sfoura@10.16.20.2

# Connect TigerVNC Viewer
vncviewer localhost:5910
```
