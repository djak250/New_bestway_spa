## Bestway Smart Spa (Custom Component)

This Home Assistant integration allows you to control your Bestway SmartHub-enabled spa via the Bestway cloud API.

---

## Installation

1. Copy the `new_bestway_spa/` folder into `custom_components/` in your Home Assistant configuration directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services** and click **Add Integration**.
4. Search for **Bestway Spa** and follow the configuration flow.

---

## Required Info

- **visitor_id**: Captured from the Bestway app using a proxy (e.g. Proxyman or HTTP Toolkit)
- **registration_id**: Also from the app proxy traffic
- **client_id**: Only required if using an Android device (`push_type: fcm`)
- **device_id** and **product_id**: Found in API calls like `/api/enduser/home/room/devices`
- **push_type**: `"fcm"` for Android, `"apns"` for iOS

 The integration automatically authenticates with the Bestway API and handles token creation internally.

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
