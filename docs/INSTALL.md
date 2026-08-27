# Installing SmartyPlants in Home Assistant

A complete walkthrough, from having no Home Assistant at all to seeing your
plants on a dashboard.

Skip ahead if you already have Home Assistant running:

- [Stage 1 — Get Home Assistant running](#stage-1--get-home-assistant-running)
- [Stage 2 — Install HACS](#stage-2--install-hacs)
- [Stage 3 — Add SmartyPlants](#stage-3--add-smartyplants)
- [Stage 4 — Connect your account](#stage-4--connect-your-account)
- [Stage 5 — Check it worked](#stage-5--check-it-worked)

---

## Before you start

**Home Assistant is software you run yourself**, on a device in your home. The
Home Assistant phone app does not run it — the app is a window onto a server you
already have. If you have no server, start at Stage 1.

You will need:

- Somewhere to run Home Assistant (Stage 1 covers the options)
- A free GitHub account — used once, to install HACS
- A SmartyPlants account with at least one sensor

Set aside about an hour for a first-time setup, most of it waiting for things to
boot.

---

## Stage 1 — Get Home Assistant running

Pick whichever suits you. If you have no strong preference, the first option is
the least work.

### Option A: Buy a ready-made box

**Home Assistant Green** is a small device you plug into your router. It arrives
with everything installed. Power it on, and skip to "First-time setup" below.

Home Assistant Yellow is the same idea with more expansion options.

### Option B: Raspberry Pi

A Raspberry Pi 4 or 5 with a microSD card or SSD.

1. Download and open the **Raspberry Pi Imager**
2. Choose **Other specific-purpose OS → Home Assistant → Home Assistant OS**
3. Write it to the card, put it in the Pi, connect ethernet, power on

### Option C: Docker, NAS, or an existing server

If you already run Docker, follow the container instructions in the Home
Assistant documentation. This route is more flexible but assumes you are
comfortable with Docker.

### First-time setup

1. Wait about five minutes after powering on
2. On a computer on the same network, open **http://homeassistant.local:8123**
   (if that does not resolve, use the device's IP address)
3. Create your account, name your home, and finish the onboarding

You now have Home Assistant. Optionally install the **Home Assistant** app on
your phone and point it at the same address.

---

## Stage 2 — Install HACS

HACS (the Home Assistant Community Store) is how Home Assistant installs
integrations that are not built in. SmartyPlants is distributed through it while
our submission to Home Assistant core is in review.

This stage runs **on the Home Assistant machine**, not on your laptop.

1. In Home Assistant: **Settings → Add-ons → Add-on Store**
2. Find **Terminal & SSH**, then **Install** and **Start**
3. Open its **Web UI** and run:

   ```bash
   wget -O - https://get.hacs.xyz | bash -
   ```

4. Restart Home Assistant: **Settings → System → ⋮ (top right) → Restart Home
   Assistant**. Wait for it to come back.
5. **Settings → Devices & Services → + Add integration**, search **HACS**
6. Tick the acknowledgements, then authorise with GitHub: it shows a code to
   enter at **github.com/login/device**

**HACS now appears in your sidebar.** If it does not, the restart in step 4 did
not complete — restart again and wait longer.

---

## Stage 3 — Add SmartyPlants

1. Open **HACS** in the sidebar
2. Top right **⋮ → Custom repositories**
3. Paste this repository URL:

   ```
   https://github.com/smartyplantstech/homeassistant-smartyplants
   ```

4. Set **Type: Integration**, then **Add**
5. Search HACS for **SmartyPlants**, open it, and choose **Download**
6. Restart Home Assistant again

---

## Stage 4 — Connect your account

There is no configuration file to edit. Everything happens in the interface.

1. In the SmartyPlants app: **Settings**, then create an **API key** and copy it
2. In Home Assistant: **Settings → Devices & Services → + Add integration**
3. Search **SmartyPlants**
4. Leave **Server** as it is, paste your **API key**, and submit

That is the setup finished. Your plants appear as devices, each placed in the
room matching its environment in the app.

### Optional: live updates

By default Home Assistant checks for new readings every minute. To have them
arrive the moment a sensor reports:

1. On the second step of setup, copy the **webhook URL** shown
2. Add it in the SmartyPlants app as your Home Assistant webhook
3. Paste the **signing secret** the app gives you back, into the same dialog

Leaving the secret empty is perfectly fine — it just means readings arrive on the
one-minute schedule. Live updates also require your Home Assistant to be
reachable from the internet.

---

## Stage 5 — Check it worked

Go to **Settings → Devices & Services → SmartyPlants**. You should see one device
per plant.

Open one. Each plant provides:

| Entity | What it shows |
| ------ | ------------- |
| Temperature | Air temperature at the plant |
| Humidity | Relative humidity |
| Soil moisture | Moisture in the soil |
| Illuminance | Light reaching the plant, in lux |
| Light quality | How suitable that light is for the species, 0–100 |
| Health score | Overall plant health, 0–100 |
| Fertilise in | Days until fertilising is due |
| Status | What, if anything, needs your attention |

Battery, last reported, connectivity and a stale-readings flag are also there,
grouped as diagnostics.

### If entities show "Unavailable"

That is deliberate. Readings older than three hours are hidden rather than shown
as if current. Check **Last reported** and **Battery** on the device — a flat
battery or a sensor out of range is the usual cause.

### What the Status entity is telling you

| Status | What to do |
| ------ | ---------- |
| OK | Nothing — it is working |
| Add a sensor in the app | The plant has no sensor attached yet |
| Add a plant in the app | The sensor is not assigned to a plant yet |
| Waiting for first readings | Nothing; readings arrive within a few minutes |
| Sensor offline | Check the sensor's battery and range |
| Readings outdated | The sensor has not reported for over three hours |

---

## Common problems

**"Could not reach the SmartyPlants server."**
Check your internet connection and that the **Server** field is unchanged from
the default.

**"That API key was rejected."**
The key was revoked or mistyped. Create a new one in the app under Settings.

**SmartyPlants does not appear in the Add integration list.**
The restart after downloading from HACS did not complete. Restart Home Assistant
and try again.

**A plant appears with no readings.**
It has no sensor attached. Attach one in the SmartyPlants app; readings appear
here within a few minutes.

---

## Getting help

Open an issue at
<https://github.com/smartyplantstech/homeassistant-smartyplants/issues>,
including your Home Assistant version and what the **Status** entity shows.
