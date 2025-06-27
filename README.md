## Bestway Smart Spa (Custom Component)

This Home Assistant integration allows you to control your Bestway SmartHub-enabled spa via the Bestway cloud API.

---

## Installation

1. Copy the `new_bestway_spa/` folder into `custom_components/` in your Home Assistant configuration directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services** and click **Add Integration**.
4. Search for **Bestway Spa** and follow the configuration flow.

---

## Prerequisites

### Required Equipment
- A **PC or Mac** with [Charles Proxy](https://www.charlesproxy.com/download/) installed
- Two smartphones (Android or iOS):
  - **Phone A**: with the Bestway Smart Hub app installed and already connected to your spa (used to share the QR code)
  - **Phone B**: used to capture traffic through Charles Proxy (the SSL certificate will be installed on this device)

### Network
- PC and both smartphones must be connected to the **same Wi-Fi network**

---

## Step 1 – Setup Charles Proxy

1. Launch **Charles Proxy** on your PC
2. Go to `Proxy > Proxy Settings` and note the HTTP port (default: `8888`)
3. Go to `Help > SSL Proxying > Install Charles Root Certificate` (install it on your PC)

---

## Step 2 – Configure Phone B

### A. Set Wi-Fi Proxy
- On **Phone B**, go to Wi-Fi settings
- Long press the connected network > Modify > Advanced options
- Set Proxy to **Manual**:
  - **Proxy host**: your PC’s IP address
  - **Port**: `8888`

### B. Install SSL Certificate
> Required to decrypt HTTPS traffic

#### Android (to be confirmed)
- Visit `http://charlesproxy.com/getssl` on Phone B
- Download the certificate
- Install it: `Settings > Security > Encryption & credentials > Install from storage`

#### iOS
- Open Safari: [https://chls.pro/ssl](https://chls.pro/ssl)
- Accept and install the profile
- Go to: `Settings > General > VPN & Device Management > Charles Proxy CA`
- Enable in: `Settings > General > About > Certificate Trust Settings`

---

## Step 3 – Enable SSL Proxying

In Charles:
1. Go to `Proxy > SSL Proxying Settings`
2. Click **Add**
3. Set:
   - Host: `*`
   - Port: `443`

---

## Step 4 – Capture the Data

1. Close the Bestway Smart Hub app on **Phone B**
2. Start recording in Charles (click the **●** button)
3. Open the Bestway Smart Hub app again
4. Select **United Kingdom** region and scan the QR code
5. Watch for requests like `thing_shadow`, `command`, or to `api.bestwaycorp`

---

## Step 5 – Retrieve Credentials

1. Look for a **POST** request to `/enduser/visitor`:
   - [https://smarthub-eu.bestwaycorp.com](https://smarthub-eu.bestwaycorp.com)
2. Open it and check **Request > JSON** or **Text**

### Useful credentials to extract:
- `visitor_id`
- `client_id` (for Android)
- `device_id`
- `product_id`

### Additional:
- `registration_id` and `client_id` can be found in `/api/enduser/visitor`
- `device_id` and `product_id` may be in `/api/enduser/home/room/devices`

---

## Cleanup

- Disable the proxy on Phone B
- Remove the Charles SSL certificate if no longer needed



---

## Configuration Options

| Field            | Required | Notes                                      |
|------------------|----------|--------------------------------------------|
| `device_name`    | ✅       | Display name in Home Assistant             |
| `visitor_id`     | ✅       | From intercepted app traffic               |
| `registration_id`| ✅       | Same as above                              |
| `client_id`      | ❌       | Only for Android (`push_type = fcm`)       |
| `device_id`      | ✅       | Needed to control the spa                  |
| `product_id`     | ✅       | Needed to control the spa                  |
| `push_type`      | ❌       | `fcm` (Android) or `apns` (iOS), default `fcm` |

---

## API Notes

- `filter_state` returns `2` when active, `0` when off — the integration handles this automatically.
- `select` gives the possibility to choose  the bubble/wave mode OFF/L1/L2 (not available from the official app)
- To **turn on** any feature, the integration sends `1`. To **turn off**, it sends `0`.
- All values are polled from `/api/device/thing_shadow/`

---

## Features

- Toggle spa power, filter, heater, and wave jets
- Adjust water target temperature
- View current water temperature
- Monitor connection status, warnings, and error codes

---

## Example Lovelace Card

```yaml
type: entities
title: Spa Bestway
entities:
  - switch.spa_bestway_spa_power
  - switch.spa_bestway_filter
  - switch.spa_bestway_heater
  - switch.spa_bestway_bubbles_wave
  - number.spa_bestway_target_temperature
  - sensor.spa_bestway_water_temperature
  - sensor.spa_bestway_warning
  - sensor.spa_bestway_error_code
  - sensor.spa_bestway_is_online
```

## Disclaimer
This is a community-made integration. It is not affiliated with or endorsed by Bestway.
Use at your own risk — the code interacts with a private API which may change.
