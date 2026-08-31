"""Config flow for SmartyPlants — this is what replaces configuration.yaml."""

from collections.abc import Mapping
from typing import Any, override

from pysmartyplants import (
    SmartyPlantsAuthError,
    SmartyPlantsClient,
    SmartyPlantsConnectionError,
)
import voluptuous as vol

from homeassistant.components import webhook as hass_webhook
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_WEBHOOK_ID
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_WEBHOOK_SECRET, DEFAULT_HOST, DOMAIN

# Everyone connects to the SmartyPlants service, so the address is never asked
# for. Entries still carry it, which keeps existing installations working and
# leaves one place to change when developing against another backend.
CREDENTIALS_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})


# The secret is optional: without it the integration still polls, it just
# cannot verify pushes, so it refuses them.
STEP_WEBHOOK_SCHEMA = vol.Schema({vol.Optional(CONF_WEBHOOK_SECRET): str})


class SmartyPlantsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the UI setup dialog."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise the flow state."""
        self._data: dict[str, Any] = {}

    async def _async_validate(
        self, host: str, api_key: str
    ) -> tuple[str | None, str | None]:
        """Return (error key, account id); exactly one is set."""
        client = SmartyPlantsClient(
            api_key, host=host, session=async_get_clientsession(self.hass)
        )
        try:
            account_id = await client.async_verify()
        except SmartyPlantsAuthError:
            return "invalid_auth", None
        except SmartyPlantsConnectionError:
            return "cannot_connect", None
        return None, account_id

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Prompt for host and API key, then verify them."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = DEFAULT_HOST
            error, account_id = await self._async_validate(
                host, user_input[CONF_API_KEY]
            )
            if error:
                errors["base"] = error
            else:
                # Keyed on the account, not the API key: a rotated key is the
                # same account and must not create a second entry.
                await self.async_set_unique_id(account_id)
                self._abort_if_unique_id_configured()

                self._data = {
                    CONF_API_KEY: user_input[CONF_API_KEY],
                    CONF_HOST: host,
                    CONF_WEBHOOK_ID: hass_webhook.async_generate_id(),
                }
                return await self.async_step_webhook()

        return self.async_show_form(
            step_id="user",
            data_schema=CREDENTIALS_SCHEMA,
            errors=errors,
        )

    async def async_step_webhook(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show the push URL and collect the signing secret.

        The backend's webhook endpoints are user-authenticated rather than
        API-key authenticated, so Home Assistant cannot register itself. The
        user pastes this URL into the SmartyPlants app, which hands back the
        secret they enter here.
        """
        if user_input is not None:
            secret = user_input.get(CONF_WEBHOOK_SECRET)
            return self.async_create_entry(
                title="SmartyPlants",
                data={
                    **self._data,
                    **({CONF_WEBHOOK_SECRET: secret} if secret else {}),
                },
            )

        return self.async_show_form(
            step_id="webhook",
            data_schema=STEP_WEBHOOK_SCHEMA,
            description_placeholders={
                "webhook_url": hass_webhook.async_generate_url(
                    self.hass, self._data[CONF_WEBHOOK_ID]
                )
            },
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Let the user change the server or API key of an existing entry."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            host = DEFAULT_HOST
            error, account_id = await self._async_validate(
                host, user_input[CONF_API_KEY]
            )
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(account_id)
                self._abort_if_unique_id_mismatch(reason="account_mismatch")

                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_API_KEY: user_input[CONF_API_KEY],
                        CONF_HOST: host,
                    },
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                CREDENTIALS_SCHEMA, entry.data
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Start the re-auth prompt when the key stops working."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for a fresh API key against the already-configured host."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            error, account_id = await self._async_validate(
                entry.data.get(CONF_HOST, DEFAULT_HOST), user_input[CONF_API_KEY]
            )
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(account_id)
                self._abort_if_unique_id_mismatch(reason="account_mismatch")

                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_API_KEY: user_input[CONF_API_KEY]}
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )
