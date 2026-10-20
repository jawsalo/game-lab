"""Tests for optional OpenTelemetry configuration."""

from __future__ import annotations

import unittest

from apps.api.app.telemetry import (
    configured_signal_endpoint,
    resource_attributes,
    signal_endpoint,
)


class TelemetryConfigurationTests(unittest.TestCase):
    def test_signal_endpoint_prefers_signal_specific_value(self) -> None:
        environment = {
            "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector:4317",
            "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT": "http://traces:4317",
        }

        self.assertEqual(
            signal_endpoint(environment, "traces"),
            "http://traces:4317",
        )
        self.assertEqual(
            signal_endpoint(environment, "metrics"),
            "http://collector:4317",
        )

    def test_signal_endpoint_is_optional(self) -> None:
        self.assertIsNone(signal_endpoint({}, "traces"))

    def test_non_otlp_exporter_disables_signal(self) -> None:
        self.assertIsNone(
            configured_signal_endpoint(
                {
                    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector:4317",
                    "OTEL_TRACES_EXPORTER": "none",
                },
                "traces",
            )
        )

    def test_resource_identity_uses_application_environment(self) -> None:
        self.assertEqual(
            resource_attributes(
                {
                    "OTEL_SERVICE_NAME": "game-lab-api",
                    "APP_VERSION": "9fc6cbd",
                    "APP_ENV": "production",
                }
            ),
            {
                "service.name": "game-lab-api",
                "service.version": "9fc6cbd",
                "deployment.environment.name": "production",
            },
        )


if __name__ == "__main__":
    unittest.main()
