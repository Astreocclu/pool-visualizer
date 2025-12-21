"""Tests for roofs tenant configuration."""
import pytest
from api.tenants.roofs.config import (
    RoofsTenantConfig,
    get_config,
    get_full_config_with_pricing,
    ROOF_MATERIALS,
    SOLAR_OPTIONS,
)


class TestRoofsConfig:
    """Test roofs configuration."""

    def test_tenant_id(self):
        config = RoofsTenantConfig()
        assert config.tenant_id == 'roofs'

    def test_display_name(self):
        config = RoofsTenantConfig()
        assert config.display_name == 'Roofs & Solar'

    def test_pipeline_steps(self):
        config = RoofsTenantConfig()
        steps = config.get_pipeline_steps()
        assert steps == ['cleanup', 'roof_material', 'solar_panels', 'gutters_trim', 'quality_check']

    def test_step_configs_exist(self):
        config = RoofsTenantConfig()
        for step in config.get_pipeline_steps():
            step_config = config.get_step_config(step)
            assert step_config, f"Missing config for step: {step}"
            assert 'type' in step_config

    def test_roof_materials_have_required_fields(self):
        for material in ROOF_MATERIALS:
            assert 'id' in material
            assert 'name' in material
            assert 'prompt_hint' in material

    def test_solar_options_have_required_fields(self):
        for option in SOLAR_OPTIONS:
            assert 'id' in option
            assert 'name' in option

    def test_get_config_excludes_pricing(self):
        config = get_config()
        for material in config['roof_materials']:
            assert 'price_per_sqft' not in material

    def test_get_full_config_includes_pricing(self):
        config = get_full_config_with_pricing()
        # At least one material should have pricing
        has_pricing = any('price_per_sqft' in m for m in config['roof_materials'])
        assert has_pricing
