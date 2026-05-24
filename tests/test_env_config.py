# tests/test_env_config.py — Tests for taskflow/env_config.py
import os
import pytest
from pathlib import Path
from taskflow.env_config import get_settings, Settings


class TestGetSettings:
    def test_returns_settings_object(self):
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_singleton_same_instance(self):
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_reload_returns_new_instance(self):
        s1 = get_settings()
        s2 = get_settings(reload=True)
        assert s1 is not s2

    def test_test_env_user_name(self):
        # .env.test sets TASKFLOW_USER_NAME=TestUser
        settings = get_settings(reload=True)
        assert settings.user_name == "TestUser"

    def test_test_env_weather_disabled(self):
        # .env.test sets TASKFLOW_WEATHER=false
        settings = get_settings(reload=True)
        assert settings.weather_enabled is False

    def test_test_env_log_file_disabled(self):
        # .env.test sets TASKFLOW_LOG_FILE=false
        settings = get_settings(reload=True)
        assert settings.log_to_file is False

    def test_env_override_takes_precedence(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_USER_NAME", "OverrideUser")
        settings = get_settings(reload=True)
        assert settings.user_name == "OverrideUser"

    def test_plan_lowercased(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_USER_PLAN", "PREMIUM")
        settings = get_settings(reload=True)
        assert settings.user_plan == "premium"

    def test_data_file_path_type(self):
        settings = get_settings()
        assert isinstance(settings.data_file, Path)

    def test_log_dir_type(self):
        settings = get_settings()
        assert isinstance(settings.log_dir, Path)

    def test_latitude_float(self):
        settings = get_settings()
        assert isinstance(settings.user_latitude, float)

    def test_longitude_float(self):
        settings = get_settings()
        assert isinstance(settings.user_longitude, float)

    def test_no_api_keys_in_test_env(self):
        settings = get_settings()
        assert settings.anthropic_api_key == ""
        assert settings.openai_api_key    == ""

    def test_has_ai_key_false_when_empty(self):
        settings = get_settings()
        assert settings.has_ai_key() is False

    def test_has_ai_key_true(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake-key")
        settings = get_settings(reload=True)
        assert settings.has_ai_key() is True

    def test_is_debug_false_by_default(self):
        settings = get_settings(reload=True)
        # .env.test sets TASKFLOW_DEBUG=false and LOG_LEVEL=WARNING
        assert settings.is_debug() is False

    def test_is_debug_true_when_debug_set(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_DEBUG", "true")
        settings = get_settings(reload=True)
        assert settings.is_debug() is True

    def test_settings_frozen(self):
        """Settings is a frozen dataclass — attributes cannot be changed."""
        settings = get_settings()
        with pytest.raises((AttributeError, TypeError)):
            settings.user_name = "MutatedName"  # type: ignore[misc]

    def test_repr_does_not_expose_keys(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-super-secret")
        settings = get_settings(reload=True)
        r = repr(settings)
        assert "sk-ant" not in r

    def test_invalid_float_falls_back_to_default(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_LATITUDE", "not-a-number")
        settings = get_settings(reload=True)
        assert settings.user_latitude == 28.6139   # default


class TestSettingsDataDir:
    def test_data_file_inside_data_dir(self):
        settings = get_settings()
        assert settings.data_file.parent == settings.data_dir

    def test_custom_data_dir(self, monkeypatch, tmp_path):
        monkeypatch.setenv("TASKFLOW_DATA_DIR", str(tmp_path))
        settings = get_settings(reload=True)
        assert settings.data_dir == tmp_path

    def test_custom_data_filename(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_DATA_FILENAME", "my_tasks.json")
        settings = get_settings(reload=True)
        assert settings.data_file.name == "my_tasks.json"