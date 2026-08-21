# SmartyPlants for Home Assistant

Connects your [SmartyPlants](https://smartyplants.com) plant sensors to Home
Assistant. Each plant becomes a device with its readings as entities, so you can
chart them, put them on a dashboard, and build automations — a notification when
the soil dries out, a grow light when the day has been dim.

> This is the custom-integration release. A pull request to include SmartyPlants
> in Home Assistant core is in progress; until it is merged, install it here.

## Install

**New to Home Assistant?** Start with the [full installation guide](docs/INSTALL.md),
which covers setting up Home Assistant itself, then HACS, then this integration.

Already running Home Assistant with HACS? Continue below.

### HACS (recommended)

1. In HACS, open the three-dot menu → **Custom repositories**
2. Add `https://github.com/smartyplantstech/homeassistant-smartyplants` with type
   **Integration**
3. Search for **SmartyPlants** and install it
4. Restart Home Assistant

### Manually

1. Download the latest release
2. Copy `custom_components/smartyplants` into your Home Assistant `config/custom_components/`
3. Restart Home Assistant

## Set up

There is no YAML configuration. After restarting:

1. **Settings → Devices & Services → + Add integration**
2. Search for **SmartyPlants**
3. Paste the API key from the SmartyPlants app, under **Settings**
4. Optionally paste a webhook secret for live updates (see below)

Your plants appear as devices, each in the area matching its environment in the
app.

## Live updates

By default the integration polls every 10 minutes. For updates the moment a
sensor reports:

1. Copy the webhook URL shown on the second step of setup
2. Add it in the SmartyPlants app as your Home Assistant webhook
3. Paste the signing secret it gives you back into the setup dialog

Pushes are verified against that secret, so an unsigned or wrongly signed update
is rejected. Polling continues as a fallback either way, so leaving the secret
empty is a supported choice — it just means updates arrive on the poll.

Home Assistant must be reachable from the internet for a webhook to be delivered.

## Entities

Per plant: temperature, humidity, soil moisture, illuminance, light quality,
health score, fertilise countdown, and a status entity. Plus diagnostics —
battery, last reported, connectivity, and whether the readings have gone stale.

### Status

| State | Meaning |
| ----- | ------- |
| OK | Everything is working |
| Add a sensor in the app | The plant has no sensor attached |
| Add a plant in the app | The sensor is not assigned to a plant |
| Waiting for first readings | Paired, but nothing has arrived yet |
| Sensor offline | The sensor has stopped reporting |
| Readings outdated | The last reading is over three hours old |

A plant with no sensor still appears, showing only its status, so you can see the
whole collection in one place.

## Data handling

Readings older than three hours are treated as unreliable: the measurement
entities go unavailable rather than keep showing values that no longer describe
the plant. Battery and last-reported keep reporting so you can see why.

Plants and sensors added or removed in the app are picked up automatically. No
reload or restart needed.

## Requirements

- Home Assistant 2026.8.0 or newer
- A SmartyPlants account with an API key
