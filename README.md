🔥 ProStream OME: Low-Latency Broadcast Station

ProStream OME is a high-performance, self-hosted streaming solution designed to deliver broadcast-quality video with sub-second latency.

It bypasses the limitations of browser-based capture (WebRTC getDisplayMedia) by leveraging OBS Studio for high-fidelity hardware encoding (NVENC/AV1) and OvenMediaEngine for ultra-low-latency distribution.

🏗 System Architecture

The system consists of three main components:

graph LR
    A[🖥️ Game/Desktop] -->|Capture| B(OBS Studio)
    B -->|RTMP Ingest| C{OvenMediaEngine}
    C -->|WebRTC Stream| D[Your Browser]
    C -->|WebRTC Stream| E[Friend's Browser]
    
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#65f,stroke:#333,stroke-width:2px,color:#fff


Source (Host): OBS Studio captures the screen and encodes it (H.264/AV1).

Server (Docker): OvenMediaEngine receives the stream and transmuxes it to WebRTC.

Client (Viewer): A custom HTML5 player connects via WebRTC for playback.

🚀 Prerequisites

Hardware: A PC capable of running Docker Desktop and OBS Studio simultaneously.

Software:

Docker Desktop (Running in background)

OBS Studio

Network: Ability to port forward (if streaming over the internet).

🛠️ Installation & Setup

1. Start the Server (Docker)

Create a folder for your project.

Save the provided docker-compose.yml file inside it.

Open a terminal/PowerShell in that folder.

Run the following command to start the engine:

docker-compose up -d


2. Configure Network (Port Forwarding)

If you want friends to connect from outside your home network, log into your router and forward the following ports to your host PC's IP address:

Port Range

Protocol

Purpose

1935

TCP

RTMP Ingest (OBS to Server)

3333

TCP

WebRTC Signalling (Handshake)

10000-10010

UDP

WebRTC Media Transport (Video/Audio)

Note: If testing locally on the same network, port forwarding is not required.

📹 OBS Studio Configuration

Configure OBS to send a low-latency stream to your local Docker container.

Open Settings -> Stream.

Service: Custom...

Server: rtmp://localhost:1935/app

Stream Key: stream

Open Settings -> Output (Set Output Mode to Advanced).

Encoder: NVIDIA NVENC H.264 (or AV1 if available/supported).

Rate Control: CBR (Constant Bitrate).

Bitrate: 6000 Kbps (up to 20000 Kbps for high quality).

Keyframe Interval: 1 s <span style="color:red">(CRITICAL)</span>.

Setting this to 0 or Auto will cause massive latency buffering.

Preset: P1 or P2 (Fastest/Low Latency).

Tuning: Ultra Low Latency.

Multipass Mode: Single Pass.

🌐 Viewer Configuration

Host the Web Player:

You can host the index.html file on GitHub Pages, Netlify, or a simple local server (python -m http.server).

Connect:

Open the hosted page.

Click the Gear Icon ⚙️.

Host: Enter your Public IP (e.g., 104.6.x.x) if sharing, or localhost if testing.

Click Connect.

🔧 Troubleshooting

Docker Errors

Error: "error during connect: This error may indicate that the docker daemon is not running."

Fix: Launch Docker Desktop from your Start menu and wait for the icon to appear in the system tray.

Black Screen / Connection Failed

Symptom: The player says "Live" but shows black, or spins forever.

Fix: This is almost always a firewall/port issue. Ensure UDP ports 10000-10010 are forwarded on your router and allowed through Windows Firewall.

High Latency (>2 seconds)

Fix: Check your OBS Output settings. Ensure Keyframe Interval is set to exactly 1s.