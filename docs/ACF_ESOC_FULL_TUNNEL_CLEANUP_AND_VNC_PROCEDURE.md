# INDUSTRIAL HPC PROCEDURAL GUIDE: SSH TUNNEL CLEANUP & VNC DISPLAY FOR ACF ESOC

**Role:** Senior HPC Infrastructure Engineer  
**Host HPC:** `sms1` (`10.16.20.2`)  
**User:** `sfoura`  
**Workspace:** `/onm/dem/home/sfoura/ACF`  
**Client PC:** Ubuntu Desktop  
**Environment:** `conda activate acf-hpc`  

---

## 1. COMPREHENSIVE DIAGNOSIS

The error `bind [127.0.0.1]:5910: Address already in use` on your local Ubuntu PC occurs because an old `ssh` process (PID `162177` or orphaned background thread) is still holding local port `5910` open in TIME_WAIT / LISTEN state.

Because multiple background SSH tunnels (`-L 5900:localhost:5900`, `-X`, `-N -L 5910:localhost:5910`) were created across multiple terminals, the local sockets on ports 5900-5910 became locked on your Ubuntu PC while `QVncServer` was listening on `sms1`.

---

## 2. PHASE 1 — COMPLETE CLEANUP ON CLIENT UBUNTU PC

Run these exact commands in a terminal on your **local Ubuntu PC**:

```bash
# 1. Kill all background SSH tunnel processes on your Ubuntu PC
pkill -f "ssh.*10.16.20.2"

# 2. Force kill any remaining SSH processes holding ports 5900-5915
fuser -k 5900/tcp 5910/tcp 5911/tcp 2>/dev/null || true

# 3. Kill local TigerVNC viewers if any are frozen
pkill -9 -f "vncviewer"

# 4. Verify local ports 5900 and 5910 are completely FREE
ss -tulpn | grep -E "5900|5910"
# Expected output: (EMPTY - No process listening)
```

---

## 3. PHASE 2 — CLEANUP AND LAUNCH ON HPC (`sms1`)

Open a **single new SSH terminal** to `sms1`:

```bash
# Connect to sms1
ssh sfoura@10.16.20.2

# 1. Kill any old Python ACF or Qt VNC processes on sms1
pkill -u sfoura -f "acf.gui.app"
pkill -u sfoura -f "python"

# 2. Verify ports 5900 and 5910 are FREE on sms1
ss -tulpn | grep -E "5900|5910"
# Expected output: (EMPTY)

# 3. Activate Conda Environment & Set PYTHONPATH
conda activate acf-hpc
export PYTHONPATH=/onm/dem/home/sfoura/ACF/src:$PYTHONPATH

# 4. Launch Qt QVncServer explicitly on Port 5910
export QT_QPA_PLATFORM="vnc:size=1920x1080:port=5910"
python -m acf.gui.app
```

**Output on `sms1`:**  
`QVncServer created on port 5910`  
*(Leave this terminal running in the foreground).*

---

## 4. PHASE 3 — ESTABLISH SSH TUNNEL FROM LOCAL UBUNTU PC

Open a **second terminal** on your **local Ubuntu PC**:

```bash
# Establish clean SSH tunnel (forwarding local 5910 to sms1 5910)
ssh -N -L 5910:localhost:5910 sfoura@10.16.20.2
```

*(Leave this tunnel running in the background/terminal).*

---

## 5. PHASE 4 — LAUNCH TIGERVNC VIEWER ON LOCAL UBUNTU PC

Open a **third terminal** on your **local Ubuntu PC**:

```bash
# Verify local port 5910 is bound by the new SSH tunnel
ss -tulpn | grep 5910
# Expected output: tcp LISTEN 127.0.0.1:5910 (ssh)

# Launch TigerVNC Viewer connecting to local tunnel
vncviewer localhost:5910 -CompressionLevel 2 -QualityLevel 6
```

---

## 5. RESULT & VERIFICATION

TigerVNC opens a 1920x1080 window displaying the live interactive **ACF v1.0.0 GESOP ESOC Command Center Dashboard**.
