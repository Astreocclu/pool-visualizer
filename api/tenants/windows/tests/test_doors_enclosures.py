"""Tests for windows tenant door and enclosure prompts."""
import pytest
from api.tenants.windows import prompts
from api.tenants.windows.config import WindowsTenantConfig, DOOR_TYPES, PATIO_ENCLOSURE_TYPES


class TestWindowsConfig:
    """Test windows configuration with doors and enclosures."""

    def test_pipeline_has_7_steps(self):
        config = WindowsTenantConfig()
        steps = config.get_pipeline_steps()
        assert len(steps) == 7
        assert 'doors' in steps
        assert 'patio_enclosure' in steps

    def test_doors_step_config_exists(self):
        config = WindowsTenantConfig()
        step_config = config.get_step_config('doors')
        assert step_config != {}
        assert step_config.get('type') == 'insertion'

    def test_patio_enclosure_step_config_exists(self):
        config = WindowsTenantConfig()
        step_config = config.get_step_config('patio_enclosure')
        assert step_config != {}
        assert step_config.get('type') == 'insertion'

    def test_door_types_have_required_fields(self):
        for door in DOOR_TYPES:
            assert 'id' in door
            assert 'name' in door

    def test_enclosure_types_have_required_fields(self):
        for enclosure in PATIO_ENCLOSURE_TYPES:
            assert 'id' in enclosure
            assert 'name' in enclosure


class TestWindowsDoorPrompts:
    """Test door prompts."""

    def test_doors_prompt_returns_none_when_no_door_type(self):
        result = prompts.get_doors_prompt({})
        assert result is None

    def test_doors_prompt_returns_none_when_door_type_none(self):
        result = prompts.get_doors_prompt({'door_type': 'none'})
        assert result is None

    def test_doors_prompt_returns_string_when_door_selected(self):
        result = prompts.get_doors_prompt({
            'door_type': 'sliding_glass',
        })
        assert isinstance(result, str)
        assert 'sliding' in result.lower()

    def test_accordion_door_includes_folding_details(self):
        result = prompts.get_doors_prompt({
            'door_type': 'accordion',
        })
        assert isinstance(result, str)
        assert 'accordion' in result.lower() or 'fold' in result.lower()


class TestWindowsEnclosurePrompts:
    """Test patio enclosure prompts."""

    def test_enclosure_prompt_returns_none_when_no_type(self):
        result = prompts.get_patio_enclosure_prompt({})
        assert result is None

    def test_enclosure_prompt_returns_none_when_type_none(self):
        result = prompts.get_patio_enclosure_prompt({'enclosure_type': 'none'})
        assert result is None

    def test_enclosure_prompt_returns_string_when_selected(self):
        result = prompts.get_patio_enclosure_prompt({
            'enclosure_type': 'four_season',
        })
        assert isinstance(result, str)
        assert 'sunroom' in result.lower() or 'enclosure' in result.lower()

    def test_screen_room_includes_mesh_details(self):
        result = prompts.get_patio_enclosure_prompt({
            'enclosure_type': 'screen_room',
        })
        assert isinstance(result, str)
        assert 'screen' in result.lower()


class TestWindowsGetPromptRouter:
    """Test get_prompt includes new steps."""

    def test_doors_step_in_router(self):
        result = prompts.get_prompt('doors', {'door_type': 'french'})
        assert result is not None

    def test_patio_enclosure_step_in_router(self):
        result = prompts.get_prompt('patio_enclosure', {'enclosure_type': 'three_season'})
        assert result is not None

    def test_quality_check_includes_door_scope(self):
        result = prompts.get_quality_check_prompt({'doors': True})
        assert 'DOOR' in result or 'door' in result.lower()

    def test_quality_check_includes_enclosure_scope(self):
        result = prompts.get_quality_check_prompt({'patio_enclosure': True})
        assert 'ENCLOSURE' in result or 'enclosure' in result.lower()
