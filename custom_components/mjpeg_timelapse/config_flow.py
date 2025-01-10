import voluptuous as vol
from urllib.parse import urlparse

from homeassistant import config_entries
from homeassistant.const import (
    CONF_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import selector
from homeassistant.helpers.translation import async_get_translations

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    CONF_IMAGE_URL,
    CONF_FETCH_INTERVAL,
    CONF_MAX_FRAMES,
    CONF_FRAMERATE,
    CONF_QUALITY,
    CONF_LOOP,
    CONF_HEADERS,
    CONF_START_TIME,
    CONF_END_TIME,
    CONF_ENABLING_ENTITY_ID,
    DEFAULT_ENABLING_ENTITY_ID,  # Use the new constant
)

def valid_url(url):
    result = urlparse(url)
    return result.scheme != '' and result.netloc != ''

async def get_data_schema(hass):
    translations = await async_get_translations(hass, "en", "strings.json", DOMAIN)
    return vol.Schema(
        {
            vol.Required(CONF_IMAGE_URL): str,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Optional(CONF_FETCH_INTERVAL, default=60): int,
            vol.Optional(CONF_START_TIME, default="00:00:00"): vol.Coerce(str),
            vol.Optional(CONF_END_TIME, default="23:59:59"): vol.Coerce(str),
            vol.Optional(CONF_ENABLING_ENTITY_ID, default=DEFAULT_ENABLING_ENTITY_ID): selector({
                "entity": {
                    "domain": ["sensor", "binary_sensor"],
                    "multiple": False
                }
            }),
            vol.Optional(CONF_FRAMERATE, default=2): int,
            vol.Optional(CONF_MAX_FRAMES, default=100): int,
            vol.Optional(CONF_QUALITY, default=75): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
            vol.Optional(CONF_LOOP, default=True): bool,
            vol.Optional(CONF_HEADERS, default={}): dict,
            vol.Optional(CONF_USERNAME): str,
            vol.Optional(CONF_PASSWORD): str,
        }
    )

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Mjpeg Timelapse."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            errors = self.validate(user_input)
            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
        data_schema = await get_data_schema(self.hass)
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    def validate(self, user_input):
        errors = {}
        image_url = user_input[CONF_IMAGE_URL]
        if not valid_url(image_url):
            errors[CONF_IMAGE_URL] = "invalid_url"
        elif self.has_image_url(image_url):
            errors[CONF_IMAGE_URL] = "already_configured"
        if user_input.get(CONF_FETCH_INTERVAL, 0) < 1:
            errors[CONF_FETCH_INTERVAL] = "below_minimum_value"
        if user_input.get(CONF_FRAMERATE, 0) < 1:
            errors[CONF_FRAMERATE] = "below_minimum_value"
        if user_input.get(CONF_MAX_FRAMES, 0) < 1:
            errors[CONF_MAX_FRAMES] = "below_minimum_value"
        if user_input.get(CONF_PASSWORD, '') != '' and user_input.get(CONF_USERNAME, '') == '':
            errors[CONF_USERNAME] = "username_required"
        return errors

    def has_image_url(self, image_url):
        image_urls = {
            entry.data[CONF_IMAGE_URL] for entry in self.hass.config_entries.async_entries(DOMAIN)
        }
        return image_url in image_urls
