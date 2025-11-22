# 🔥 GeminiStreamer: Low-Latency WebRTC Streaming

Self-hosted streaming solution for sharing gameplay/desktop with friends using **sub-second latency** WebRTC technology.

---

## 🏗 System Architecture

```
[🖥️ Your Desktop] → [OBS Studio] → [RTMP] → [Mini PC: OvenMediaEngine] → [WebRTC] → [Friend's Browser]
                                                                           ↓
                                                                   [HTTP Server :8080]
```

**Source**: OBS Studio captures screen and streams RTMP to mini PC  
**Server**: OvenMediaEngine transcodes AAC→Opus and distributes via WebRTC  
**Viewers**: Friends visit `http://YOUR_IP:8080` and watch in their browser

---

## 🚀 Quick Start

### 1️⃣ Configure Environment

Copy `.env.example` to `.env` and add your IPs:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
PUBLIC_IP=YOUR_PUBLIC_IP_HERE
MINI_PC_IP=192.168.X.X
```

### 2️⃣ Start the Server

```bash
docker-compose up -d
```

This starts OvenMediaEngine with:
- **RTMP Input** on port 1935 (from OBS)
- **WebRTC Output** on port 3333 (to browsers)
- **Media Ports** 10000-10010/UDP (WebRTC ICE)

### 3️⃣ Start the Web Server

```bash
python server.py
```

The viewer page will be available at `http://YOUR_PUBLIC_IP:8080`

### 4️⃣ Configure OBS Studio

On your **main PC**, stream to the **mini PC's local IP**:

1. **Settings** → **Stream**
   - Service: `Custom...`
   - Server: `rtmp://MINI_PC_IP:1935/app` (e.g., `rtmp://192.168.1.99:1935/app`)
   - Stream Key: `stream`

2. **Settings** → **Output** → **Streaming**
   - **Video Encoder**: NVIDIA NVENC H.264
   - **Rate Control**: CBR
   - **Bitrate**: 6000-10000 Kbps ⚠️ Lower than 20Mbps for multiple viewers!
   - **Keyframe Interval**: `1` (1 second)
   - **Preset**: Quality / Max Quality
   - **Audio Encoder**: AAC (128 kbps)

3. Click **Start Streaming**

### 5️⃣ Share with Friends

Send them this link:
```
http://YOUR_PUBLIC_IP:8080
```

They just click it and watch - no downloads needed!

---

## 🌐 Network Setup

### Port Forwarding (Required for Internet Streaming)

Forward these ports on your **router** to your **mini PC's local IP**:

| Port | Protocol | Purpose |
|------|----------|---------|
| 1935 | TCP | RTMP input (OBS → Server) |
| 3333 | TCP | WebRTC signaling |
| 8080 | TCP | Web server (viewer page) |
| 10000-10010 | UDP | WebRTC media (ICE/DTLS) |

**Find your public IP**: `curl ifconfig.me` or visit [whatismyip.com](https://www.whatismyip.com)

---

## 📂 Project Structure

```
GeminiStreamer/
├── .env                     # Your IP addresses (DO NOT COMMIT)
├── .env.example             # Template for .env
├── docker-compose.yml       # OvenMediaEngine container
├── server.py                # HTTP server for viewer page
├── requirements.txt         # Python dependencies
├── index.html               # WebRTC player page
├── origin_conf/
│   ├── Server.xml          # OME configuration
│   ├── server.crt          # SSL cert (local only)
│   └── server.key          # SSL key (local only)
├── VIEWER_INSTRUCTIONS.md   # Simple guide for friends
└── README.md
```

---

## ⚙️ Configuration

### Optimizing for Multiple Viewers

If viewers report stuttering:

1. **Lower OBS bitrate** to 6000-8000 Kbps
2. **Reduce resolution** to 1920x1080 (if streaming ultrawide)
3. **Drop to 30fps** if needed
4. **Check mini PC CPU** - AAC→Opus transcoding is active per viewer

### Changing Your Public IP

If your IP changes, update `.env`:

```bash
PUBLIC_IP=NEW_IP_HERE
```

Then restart everything:
```bash
docker-compose restart
# Stop server.py (Ctrl+C) and restart it
python server.py
```

---

## 🐛 Troubleshooting

### ❌ OBS Can't Connect to Server

**Error**: "Failed to connect to server"  
**Fix**: 
- Verify you're using mini PC's **local IP** (192.168.X.X), not public IP
- Check server: `docker logs prostream-engine`
- Confirm mini PC is on and Docker is running

### ❌ Viewers Get Connection Timeout

**Symptoms**: Browser shows "Retry X/5..."  
**Fix**:
- Verify ports 3333 TCP + 10000-10010 UDP are forwarded
- Check firewall allows these ports
- Confirm public IP is correct in `.env`
- Try from different network to test

### ❌ Stuttering with Multiple Viewers

**Symptoms**: Video freezes, buffering  
**Fix**:
- **Lower OBS bitrate** to 6000-10000 Kbps (most important!)
- Reduce resolution/framerate
- Check mini PC CPU usage isn't at 100%
- Verify upload speed is adequate (need ~10-15 Mbps per viewer)

### ❌ No Audio

**Error**: Logs show "Ignore unsupported codec (AAC)"  
**Fix**: Already fixed! Server transcodes AAC→Opus automatically

### ❌ Server Won't Start

**Error**: "Port already in use"  
**Fix**:
```bash
docker-compose down
docker-compose up -d
```

---

## 💡 Performance Tips

### Recommended OBS Settings for Multiple Viewers
- **Resolution**: 1920x1080 @ 60fps (or 30fps for lower bandwidth)
- **Bitrate**: 6000-8000 Kbps (not 20000!)
- **Encoder**: NVENC H.264
- **Preset**: Quality
- **Keyframe Interval**: 1 second
- **Audio**: AAC 128kbps

### Server Optimization
- The server transcodes AAC→Opus for WebRTC compatibility
- Each viewer gets a separate transcoded stream
- Lower bitrate = less CPU load + more simultaneous viewers

---

## 📝 Requirements

**Mini PC (Server):**
- Docker Desktop or Docker Engine
- Python 3.x with `python-dotenv`
- Ports 1935, 3333, 8080 (TCP) and 10000-10010 (UDP) forwarded

**Main PC (Streaming):**
- OBS Studio or any RTMP encoder
- Network access to mini PC

**Viewers:**
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Stable internet connection (5-10 Mbps recommended)

---

## 🌟 Built With

- [OvenMediaEngine](https://github.com/AirenSoft/OvenMediaEngine) - Open-source WebRTC streaming server
- [OvenPlayer](https://github.com/AirenSoft/OvenPlayer) - HTML5 WebRTC player  
- [Tailwind CSS](https://tailwindcss.com/) - UI framework
- Python SimpleHTTPServer - Lightweight web server

---

## 🔒 Security Notes

- `.env` file contains your IP addresses - **never commit it to GitHub**
- `.gitignore` is configured to exclude sensitive files
- Self-signed SSL certificates are for local testing only
- HTTP (not HTTPS) is used for simplicity - consider reverse proxy with Let's Encrypt for production