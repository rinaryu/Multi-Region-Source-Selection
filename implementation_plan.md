# End-to-End Source Selection Implementation Plan

This document outlines the proposed implementation plan to complete the Multi-Region Source Selection project. The goal is to establish a functional end-to-end DASH video streaming pipeline that leverages a central controller to dynamically route clients to different regional origin servers based on distance.

## Proposed Changes

---

### Packaging & Transcoding (`packaging/`)

To accurately measure Quality of Experience (QoE) drops when a bad region is selected, the video must support auto-degradation.

#### [MODIFY] [transcode.py](file:///Users/filipomarcellino/Documents/spring2026/471/termProject/Multi-Region-Source-Selection/packaging/transcode.py)
- Modify the script to output multiple resolutions forming an adaptive bitrate (ABR) ladder (e.g., 360p, 480p, 720p).

#### [MODIFY] [package.py](file:///Users/filipomarcellino/Documents/spring2026/471/termProject/Multi-Region-Source-Selection/packaging/package.py)
- Ensure all transcoded resolutions are packaged together by Bento4 into a single `stream.mpd` to support stream quality switching.

---

### Origin Servers (`origins/`)

We will build robust origin servers to be deployed globally on AWS.

#### [NEW] [origin_server.py](file:///Users/filipomarcellino/Documents/spring2026/471/termProject/Multi-Region-Source-Selection/origins/origin_server.py)
- **CORS Handling:** Implement a Python HTTP handler that explicitly allows Cross-Origin Resource Sharing (CORS).
- **Metrics/Telemetry:** Ensure the server captures connection statistics or request time if needed for deeper server-side analysis.

---

### Client Application (`client/`)

A client player using [Dash.js](https://github.com/Dash-Industry-Forum/dash.js) that can play our streams and report telemetry.

#### [NEW] [index.html](file:///Users/filipomarcellino/Documents/spring2026/471/termProject/Multi-Region-Source-Selection/client/index.html)
- A clean HTML layout containing a `<video>` element with basic UI controls.

#### [NEW] [dashjs_adapter.js](file:///Users/filipomarcellino/Documents/spring2026/471/termProject/Multi-Region-Source-Selection/client/dashjs_adapter.js)
- Initializes the player and constructs the URL to point to `http://<CONTROLLER_IP>:8000/stream.mpd?session=[id]&policy=[selected_policy]&client_region=[simulated_region]`.

#### [NEW] [headless_client.js](file:///Users/filipomarcellino/Documents/spring2026/471/termProject/Multi-Region-Source-Selection/client/headless_client.js) (or .py)
- A Puppeteer or Selenium script that will run automatically on our AWS EC2 client instances to simulate real users without requiring human clicking, and automatically ship QoE metrics back to a central log.

---

### Controller & Logic (`controller/`)

The brain of the system, responsible for modifying the DASH manifests dynamically.

#### [MODIFY] [controller_api.py](file:///Users/filipomarcellino/Documents/spring2026/471/termProject/Multi-Region-Source-Selection/controller/controller_api.py)
- Fix the `SESSIONS` versus `SESSION` typo. Extract `policy` and `client_region` query parameters. We will also add a simple backend route to ingest metrics reported by the automated clients.

#### [MODIFY] [source_selector.py](file:///Users/filipomarcellino/Documents/spring2026/471/termProject/Multi-Region-Source-Selection/controller/source_selector.py)
- Establish a mapping of AWS Origin Servers.
- **Distance Logic:** Map client origin queries to the closest AWS Region EC2 instance.
- **Alternative Policies:** Implement `round_robin` and `random` fallback algorithms for baseline performance comparisons.

#### [MODIFY] [manifest_rewriter.py](file:///Users/filipomarcellino/Documents/spring2026/471/termProject/Multi-Region-Source-Selection/controller/manifest_rewriter.py)
- Inject a `<BaseURL>` tag pointing to the origin server chosen by `source_selector.py`.

---

### Architecture & Network Emulation (AWS Distributed Approach)

Using Terraform to perform massive-scale distributed testing without local simulation.

#### [MODIFY] [infra/multi-region/main.tf](file:///Users/filipomarcellino/Documents/spring2026/471/termProject/Multi-Region-Source-Selection/infra/multi-region/main.tf)
- We will expand the existing terraform configurations to ensure we provision **two types** of EC2 instances per region:
  1. **Origin Servers:** Serving the M4S files.
  2. **Client Nodes:** Equipped with NodeJS/Puppeteer to programmatically run the `headless_client.js` script to fetch video from the origins.

## Deep Metrics Strategy

Comparing algorithms requires measuring *how* they impact User Quality of Experience (QoE). The automated clients will report telemetries to our Controller:
- **Time to First Byte (TTFB):** How fast does the manifest and first video chunk load?
- **Initial Startup Delay:** How long does the browser buffer before the video starts?
- **Rebuffering Ratio:** The percentage of time the player pauses to buffer.
- **Average Quality Chosen:** We will log what bitrate (360p, 480p, 720p) dash.js settles on. If forced across regions, quality drops. If selected optimally, quality stays high at 720p.

## Verification Plan
1. Ensure `transcode.py` generates the 3 required resolutions.
2. Ensure `pipeline.py` correctly builds the multi-bitrate ABR manifest.
3. Test locally using automated webdriver scripts to ensure metrics fire correctly.
4. Scale up the Terraform plan, spin up AWS Origins and EC2 AWS Clients.
5. Command EC2 Clients to request videos utilizing distance and round-robin policies, and capture their telemetry logs directly.
