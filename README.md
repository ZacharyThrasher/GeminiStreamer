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
# 🔥 GeminiStreamer Path B — Max-Quality Streaming on Your Main PC

This edition is built for **4K/60fps, sub-second latency** using your main PC's **Core i7 + RTX 5080**. OBS sends a pristine SRT feed locally; OvenMediaEngine (OME) handles multi-bitrate transcoding with NVENC and serves both **WebRTC (sub-second)** and **LL-HLS (~2s)** to your friends via a simple link.

---

## 🏗 Architecture

```
[OBS on Main PC] --SRT--> [OvenMediaEngine (Docker w/ NVENC)] --WebRTC--> <500 ms viewers
                                                           └--LL-HLS--> 2 s ultra-stable viewers
                                                                │
                                                   [Python HTTP server @ 8080 hosts player]
```

- **Ingest:** OBS → SRT (`srt://127.0.0.1:9999?streamid=default/app/stream`)
- **Transcode:** RTX 5080 NVENC generates 4K passthrough + 1080p60 + 720p30
- **Egress:**
  - WebRTC on ports 3333/3334 (UDP 10000-10010 + TURN 3478)
  - LL-HLS on 8085/8445 for cinema-grade reliability
- **Viewer link:** `http://PUBLIC_IP:8080` (hosted by `server.py`)

---

## 🚀 Setup Guide

### 1. Prerequisites

| Component | Notes |
|---|---|
| Docker Desktop + WSL2 | Enable GPU support (`Settings → Resources → WSL Integration → Enable GPU`). Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#windows). |
| Python 3.11+ | Used for the lightweight web server. |
| Ports forwarded | See [Network](#-%EF%B8%8F-network--port-forwarding). |

### 2. Configure Environment

```powershell
cp .env.example .env
```

Edit `.env` to contain your latest public IP:

```
PUBLIC_IP=104.6.177.38
```

### 3. Boot OvenMediaEngine + GPU pipeline

```powershell
docker compose up -d
```

Exposed services:
- `1935/tcp` (legacy RTMP fallback)
- `3333-3334/tcp` (WebRTC signaling HTTP/HTTPS)
- `3478/tcp` (built-in TURN relay)
- `8085/tcp` + `8445/tcp` (LL-HLS HTTP/HTTPS)
- `9999/udp` (SRT ingest)
- `10000-10010/udp` (WebRTC media RTP/DTLS)

### 4. Launch the Viewer Portal

Install Python dependency once:

```powershell
pip install -r requirements.txt
```

Run the HTTP server whenever you stream:

```powershell
python server.py
```

Friends will see:
```
http://PUBLIC_IP:8080
```

### 5. OBS Studio — SRT Contribution Feed

1. **Settings → Output → Streaming**
   - Encoder: `NVIDIA NVENC H.264` (or AV1/HEVC if all viewers support it)
   - Rate Control: `CBR`
   - Bitrate: `8000 Kbps` (4K source) — keep it ≤10 Mbps so multiple viewers stay smooth
   - Keyframe Interval: `1`
   - Preset: `Quality`
   - B-frames: `2`

2. **Settings → Stream**
   - Service: `Custom...`
   - Server: `srt://127.0.0.1:9999?streamid=default/app/stream`
   - No stream key needed (embedded in SRT query)
   - Optional: set **SRT Latency** to `200 ms` in OBS Advanced SRT settings for perfect error recovery.

3. Hit **Start Streaming** — the Docker container will log `SRT stream has been started`.

### 6. Share with Friends

- Send them `VIEWER_INSTRUCTIONS.md` or simply the link `http://PUBLIC_IP:8080`.
- The link never expires—no keys or tokens—so you can bookmark it once. Update `.env` only when your public IP changes.
- The web app defaults to WebRTC; LL-HLS fallback URL is provided for stubborn networks.

---

## 🧠 Understanding the New Features

### Multi-Bitrate Ladder

`origin_conf/Server.xml` now defines `max_quality_profile`:

| Track | Video | Bitrate | Audio |
|---|---|---|---|
| `source_4k` | 1:1 passthrough | whatever OBS sends | Opus 128 kbps |
| `1080p60` | NVENC H.264 1920×1080@60 | 8 Mbps | Opus 96 kbps |
| `720p30` | NVENC H.264 1280×720@30 | 4 Mbps | Opus 64 kbps |

WebRTC users always get the highest rendition their connection can sustain; LL-HLS exposes the entire ladder for manual switching in Safari/VLC.

### TURN/TCP Relay

Port 3478 keeps WebRTC working when a viewer’s network blocks high UDP ranges. Traffic falls back to TCP automatically instead of hanging at “Retry 5/5”.

### LL-HLS Fallback

`https://PUBLIC_IP:8445/app/stream/max_quality_profile/llhls.m3u8` offers a rock-solid ~2 second glass-to-glass latency. It’s ideal for mobile devices or flaky Wi-Fi where WebRTC would otherwise artifact.

### Optional Linux Kernel Tuning (if you migrate off Windows)

Add to `/etc/sysctl.conf`:

```
net.core.somaxconn = 65535
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq
```

`sudo sysctl -p` to apply. These settings unlock gigabit throughput and prevent TCP backlogs for LL-HLS.

### 🪟 Windows Host Limitations

OME runs inside Linux containers, but Windows/WSL2 hosts cannot apply the kernel-level TCP/BBR tuning above. If you need those exact sysctl values (recommended for 4K LL-HLS), deploy the stack on bare-metal Linux or a dedicated Linux VM and migrate the `origin_conf` directory there. Until then, expect the Windows networking stack to cap throughput slightly earlier than the “ideal” architecture described in the whitepaper.

---

## 📡 Network & Port Forwarding

Forward everything to **your main PC’s LAN IP**:

| Port | Protocol | Why |
|---|---|---|
| 8080 | TCP | Viewer UI (`server.py`) |
| 8085 | TCP | LL-HLS HTTP chunks |
| 8445 | TCP | LL-HLS HTTPS (Safari/iOS requires TLS) |
| 3333 | TCP | WebRTC signaling (HTTP) |
| 3334 | TCP | WebRTC signaling (HTTPS for remote browsers) |
| 3478 | TCP | TURN/TCP relay for WebRTC |
| 9999 | UDP | SRT ingest from OBS |
| 10000-10010 | UDP | WebRTC RTP media |
| 1935 (optional) | TCP | Legacy RTMP ingest fallback |

Tip: after every router reboot, verify your public IP and update `.env` if needed.

---

## 📂 Project Structure

```
GeminiStreamer/
├── .env / .env.example
├── docker-compose.yml          # GPU-enabled OME stack
├── server.py                   # Static viewer link host (port 8080)
├── requirements.txt            # python-dotenv
├── index.html                  # OvenPlayer WebRTC UI
├── VIEWER_INSTRUCTIONS.md      # Copy/paste directions for friends
├── origin_conf/
│   ├── Server.xml              # SRT ingest + ABR + LL-HLS config
│   ├── server.crt | server.key # Self-signed TLS (local only)
└── README.md
```

---

## 🐛 Troubleshooting

| Symptom | Fix |
|---|---|
| OBS says “Failed to connect to server” | Ensure OBS uses the SRT URL with streamid; confirm `docker logs -f prostream-engine` shows `SrtProvider is listening` |
| Web player stuck on “Retry 5/5” | Confirm UDP 10000-10010 forwarded. If viewer is on locked-down Wi-Fi, they can switch to LL-HLS link or rely on TURN (port 3478 must be open). |
| Audio missing | Make sure OBS output is AAC (OME transcodes to Opus). If you disabled transcoding, re-enable by keeping the provided `Server.xml`. |
| GPU not detected in container | Install NVIDIA Container Toolkit, restart Docker Desktop, and ensure `docker compose ps` shows the `NVIDIA_VISIBLE_DEVICES` env automatically injected. |
| LL-HLS 404 | The URL must include the profile: `.../app/stream/max_quality_profile/llhls.m3u8`. |
| Public link stops working overnight | Your ISP probably changed the IP. Update `.env`, re-run `docker compose up -d`, restart `server.py`. |

---

## 💡 Performance Tips

1. **Bitrate Discipline:** 8–10 Mbps looks stellar at 4K when combined with NVENC and SRT ingest. Higher bitrates eat upload headroom and cause viewer stutter.
2. **Ethernet Everything:** Keep your main PC and router on wired connections. Wi-Fi adds jitter that SRT has to mask.
3. **Monitor Logs:** `docker logs -f prostream-engine | Select-String -Pattern "SRT|WebRTC|LLHLS"` quickly shows stream status.
4. **Record Locally:** If you want VOD, set OBS to save recordings. Let OME focus on live distribution.

---

## 🌟 Built With

- [OvenMediaEngine](https://github.com/AirenSoft/OvenMediaEngine)
- [OvenPlayer](https://github.com/AirenSoft/OvenPlayer)
- [Tailwind CSS](https://tailwindcss.com/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---

Enjoy the “Path B” upgrade—your RTX 5080 is now doing the heavy lifting so your friends can watch silky 4K without touching VLC.
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

- `.env` only stores your `PUBLIC_IP`, but keep it private if you don’t want surprise viewers.
- Streams are intentionally open so one static link works forever; if you later need auth, re-enable SignedPolicy in `origin_conf/Server.xml`.
- Replace `origin_conf/server.crt` + `server.key` with real certificates (Let’s Encrypt works fine) so browsers can complete the WebRTC HTTPS/WSS handshake without scary warnings.
- Serve `index.html`/`server.py` behind HTTPS (or a reverse proxy) in production; mixed-content policies otherwise block LL-HLS on Safari/iOS.