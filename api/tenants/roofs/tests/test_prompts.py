"""Tests for roofs tenant prompts."""
import pytest
from api.tenants.roofs import prompts


class TestRoofsPrompts:
    """Test roofs prompts."""

    def test_cleanup_prompt_returns_string(self):
        result = prompts.get_cleanup_prompt()
        assert isinstance(result, str)
        assert len(result) > 100
        assert 'Texas' in result or 'roof' in result.lower()

    def test_roof_material_prompt_returns_string(self):
        result = prompts.get_roof_material_prompt({})
        assert isinstance(result, str)
        assert 'ROOF SPECIFICATIONS' in result

    def test_roof_material_prompt_includes_selection(self):
        result = prompts.get_roof_material_prompt({
            'roof_material': 'metal_standing_seam',
            'roof_color': 'charcoal'
        })
        assert 'standing seam' in result.lower()
        assert 'charcoal' in result.lower()

    def test_solar_panels_prompt_returns_none_when_no_solar(self):
        result = prompts.get_solar_panels_prompt({'solar_option': 'none'})
        assert result is None

    def test_solar_panels_prompt_returns_string_when_solar_selected(self):
        result = prompts.get_solar_panels_prompt({
            'solar_option': 'partial',
        })
        assert isinstance(result, str)
        assert 'solar' in result.lower()

    def test_gutters_prompt_returns_none_when_no_gutters(self):
        result = prompts.get_gutters_trim_prompt({'gutter_option': 'none'})
        assert result is None

    def test_gutters_prompt_returns_string_when_selected(self):
        result = prompts.get_gutters_trim_prompt({
            'gutter_option': 'copper',
        })
        assert isinstance(result, str)
        assert 'copper' in result.lower() or 'GUTTER' in result

    def test_quality_check_prompt_returns_string(self):
        result = prompts.get_quality_check_prompt()
        assert isinstance(result, str)
        assert 'JSON' in result
        assert 'score' in result.lower()

    def test_get_prompt_router_all_steps(self):
        steps = ['cleanup', 'roof_material', 'quality_check']
        for step in steps:
            result = prompts.get_prompt(step, {})
            assert result is not None, f"Step {step} returned None"

    def test_get_prompt_router_invalid_step(self):
        with pytest.raises(ValueError):
            prompts.get_prompt('invalid_step', {})
