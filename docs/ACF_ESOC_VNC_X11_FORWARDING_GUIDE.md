# PROCEDURAL GUIDE: ACF ESOC REMOTE GUI DISPLAY (VNC & X11 FORWARDING)

**Project:** Atmospheric Complexity Framework (ACF v1.0.0 GESOP)  
**Host HPC:** `sms1` (`10.16.20.2`)  
**User:** `sfoura`  
**Workspace:** `/onm/dem/home/sfoura/ACF`  
**Client OS:** Ubuntu Desktop  

---

## 1. INFRASTRUCTURE & GRAPHICS AUDIT

When running Qt/PySide6 on a headless Linux HPC login node or compute node (`sms1`), Qt requires a platform plugin (`QPA`).

When `QT_QPA_PLATFORM=vnc` is specified:
- Qt initializes its built-in `QVncServer` which opens a VNC server on port `5900` (or `5900 + display_index`).
- Qt does **NOT** require `DISPLAY` variable when using `QT_QPA_PLATFORM=vnc`.
- If "Can't open display" appears, it indicates either:
  1. An fallback attempt to use `xcb` (X11) because `QT_QPA_PLATFORM=vnc` was not set in the active shell environment.
  2. Missing libxcb / OpenGL libraries when initializing Qt offscreen layers.
  3. Port `5900` conflict on `sms1` or local PC.

---

## 2. STEP-BY-STEP DIAGNOSTIC & CONNECTION PROCEDURE

### STEP 1: Verification on HPC Host (`sms1`)

On the HPC login node (`sms1`):

```bash
# 1. Activate Environment
conda activate acf-hpc
export PYTHONPATH=/onm/dem/home/sfoura/ACF/src:$PYTHONPATH

# 2. Configure Qt VNC Platform & Specify Port Explicitly
export QT_QPA_PLATFORM=vnc:size=1920x1080:port=5900

# 3. Launch ACF ESOC Application
python -m acf.gui.app
```

Verify that the process is listening on port 5900:

```bash
# In a separate terminal on sms1:
ss -tulpn | grep 5900
# Expected output: tcp LISTEN 0 5 *:5900
```

---

### STEP 2: SSH Tunnel Setup from Local Ubuntu PC

From your local Ubuntu workstation:

```bash
# Set up SSH Tunnel forwarding local port 5900 to sms1 port 5900
ssh -N -L 5900:localhost:5900 sfoura@10.16.20.2
```

> **Tip**: If port `5900` is already in use on your local Ubuntu PC (e.g., by local screen sharing), map to local port `5901`:
> `ssh -N -L 5901:localhost:5900 sfoura@10.16.20.2` and connect `vncviewer localhost:5901`.

---

### STEP 3: TigerVNC Client Connection on Ubuntu

Install and launch TigerVNC client on your local PC:

```bash
# Install TigerVNC on Ubuntu
sudo apt-get update && sudo apt-get install -y tigervnc-viewer

# Connect TigerVNC Viewer to local SSH tunnel
vncviewer Localhost::5900 -CompressionLevel 2 -QualityLevel 6
```

---

## 3. PRODUCTION-GRADE HPC DISPLAY SOLUTIONS

For operational HPC deployments (`sms1` / Slurm nodes), we recommend two main production architectures:

### Option A: X11 Forwarding with Compression & Indirect Rendering (Simplest)
No VNC server required. Qt renders directly onto your local Ubuntu display.

```bash
# On local Ubuntu PC:
ssh -X -C sfoura@10.16.20.2

# On sms1:
conda activate acf-hpc
export PYTHONPATH=/onm/dem/home/sfoura/ACF/src:$PYTHONPATH
unset QT_QPA_PLATFORM
python -m acf.gui.app
```

### Option B: TurboVNC + VirtualGL + Slurm Interactive Jobs (Recommended for 3D/OpenGL Acceleration)
Allows multi-user isolated sessions on compute nodes with hardware GPU acceleration.

1. Launch TurboVNC server on `sms1`:
   `vncserver -geometry 1920x1080 -depth 24 :1`
2. Tunnel port 5901:
   `ssh -L 5901:localhost:5901 sfoura@10.16.20.2`
3. Connect with TurboVNC Viewer:
   `vncviewer localhost:5901`
