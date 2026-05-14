FROM homeassistant/home-assistant:stable

LABEL org.opencontainers.image.title="Marstek Venus E Home Assistant Test Image" \
      org.opencontainers.image.description="Home Assistant image with the Marstek Venus E integration preinstalled" \
      org.opencontainers.image.source="https://github.com/yuyuki/hacs_marstek_venus_e"

# Copy the integration into Home Assistant's custom_components directory.
# Build with the repository root as the Docker context.
COPY custom_components/hacs_marstek_venus_e /config/custom_components/hacs_marstek_venus_e

EXPOSE 8123
