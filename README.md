# 🔥 ProStream OME: Low-Latency Broadcast Station

ProStream OME is a high-performance, self-hosted streaming solution designed to deliver broadcast-quality video with **sub-second latency** using SRT and WebRTC.

---

## 🏗 System Architecture

```
[🖥️ Your Desktop] → [OBS Studio] → [RTMP/SRT] → [OvenMediaEngine Docker] → [SRT/WebRTC] → [Friend's VLC/Browser]
```

**Source (You)**: OBS Studio captures your screen and encodes it (H.264/HEVC/AV1)  
**Server (Docker)**: OvenMediaEngine receives RTMP/SRT and distributes via SRT or WebRTC  
**Client (Friends)**: VLC (SRT - best quality) or Browser (WebRTC - easiest)

---

## 🚀 Quick Start

### 1️⃣ Start the Server

```bash
docker-compose up -d
```

This starts OvenMediaEngine with:
- **RTMP Input** on port 1935 (for OBS)
- **WebRTC Output** on port 3333 (for viewers)
- **Media Ports** 10000-10010/UDP (for WebRTC connections)

### 2️⃣ Configure OBS Studio

1. Open **OBS Settings** → **Stream**
   - Service: `Custom...`
   - Server: `rtmp://localhost:1935/app`
   - Stream Key: `stream`

2. Open **Settings** → **Output** (Advanced mode)
   - **Encoder**: NVIDIA NVENC H.264 (or AV1 if supported)
   - **Rate Control**: CBR
   - **Bitrate**: 6000-20000 Kbps (higher = better quality)
   - **Keyframe Interval**: `1` ⚠️ **CRITICAL** - Don't use 0 or Auto!
   - **Preset**: P1/P2 (Low Latency)
   - **Tuning**: Ultra Low Latency

3. Click **Start Streaming** in OBS

### 3️⃣ Share with Your Friends

**Option A: VLC Player (⭐ Best Quality & Reliability)**

Send them the `VIEWER_INSTRUCTIONS.md` file! It has simple step-by-step instructions.

**Quick URL for VLC:**
```
srt://104.6.177.38:9998?streamid=#default#app/stream
```

They just paste this in VLC → Media → Open Network Stream

---

**Option B: Web Browser (Easiest)**

**Simply send them the `index.html` file!**

They just:
1. Download the file
2. Double-click to open it in their browser
3. The player automatically connects to your stream
4. Watch with sub-second latency! 🎉

---

## 🌐 Network Setup

### For Local Testing (Same Network)
No port forwarding needed! Friends on your local network can connect using your local IP.

### For Internet Streaming
Forward these ports on your router to your PC's local IP:

| Port Range | Protocol | Purpose |
|------------|----------|---------|
| 1935 | TCP | RTMP input from OBS |
| 3333 | TCP | WebRTC signaling |
| 9998 | UDP | SRT output (to viewers) |
| 9999 | UDP | SRT input (from OBS - optional) |
| 10000-10010 | UDP | WebRTC media transport |

**Find your public IP**: Visit [whatismyip.com](https://www.whatismyip.com)

---

## � Customization

### Change Your Public IP

If your IP changes, update it in:

**`docker-compose.yml`** (line 14):
```yaml
- OME_HOST_IP=YOUR_NEW_IP
```

**`index.html`** (line 138):
```javascript
hostInput.value = localStorage.getItem('ome_host') || 'YOUR_NEW_IP';
```

Then restart:
```bash
docker-compose restart
```

---

## 📂 Project Structure

```
GeminiStreamer/
├── docker-compose.yml       # Docker configuration
├── index.html               # Web player (share this file!)
├── origin_conf/
│   ├── Server.xml          # OvenMediaEngine config
│   ├── server.crt          # SSL cert (for future use)
│   └── server.key          # SSL key
└── README.md
```

---

## 🐛 Troubleshooting

### ❌ Docker won't start
**Error**: "docker daemon is not running"  
**Fix**: Launch **Docker Desktop** and wait for it to fully start

### ❌ Stream won't connect
**Symptoms**: Connection timeout, "failed to connect"  
**Fix**:
- Verify ports 3333 (TCP) and 10000-10010 (UDP) are forwarded
- Check Windows Firewall allows these ports
- Confirm OBS is streaming (should show green square)
- Run: `docker logs prostream-engine` to check for errors

### ❌ High latency (>2 seconds)
**Fix**: 
- Set OBS **Keyframe Interval** to exactly `1` (not 0, not auto)
- Lower your OBS bitrate if network is slow
- Check that UDP ports are open (WebRTC needs UDP)

### ❌ Black screen / no video
**Fix**:
- Verify OBS is actually streaming
- Check browser console (F12) for errors
- Ensure you're using the correct IP address
- Try refreshing the player page

---

## 💡 Tips

- **Best quality**: Use NVENC at 15-20 Mbps with keyframe=1s
- **Mobile-friendly**: Lower bitrate to 3-6 Mbps for viewers on phones
- **Multiple viewers**: OvenMediaEngine can handle dozens of simultaneous connections
- **Bookmark the player**: Friends can save the local HTML file and reuse it

---

## 📝 Requirements

- **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- **OBS Studio** or any RTMP-capable encoder
- **Modern web browser** (Chrome, Firefox, Edge, Safari)
- **Port forwarding access** (for internet streaming)

---

## 🌟 Built With

- [OvenMediaEngine](https://github.com/AirenSoft/OvenMediaEngine) - Open-source WebRTC streaming server
- [OvenPlayer](https://github.com/AirenSoft/OvenPlayer) - HTML5 WebRTC player
- [Tailwind CSS](https://tailwindcss.com/) - Modern UI framework