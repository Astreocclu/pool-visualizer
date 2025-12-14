"""Tests for tenant registry system."""
import unittest
from django.test import TestCase, override_settings

from api.tenants import (
    get_tenant_config,
    get_tenant_prompts,
    clear_cache,
    register_tenant
)
from api.tenants.pools.config import PoolsTenantConfig


class TenantRegistryTest(TestCase):

    def setUp(self):
        clear_cache()

    def test_pools_tenant_registered(self):
        """Pools tenant should be auto-registered."""
        config = get_tenant_config('pools')
        self.assertEqual(config.tenant_id, 'pools')

    def test_default_tenant_is_pools(self):
        """Default active tenant should be Pools."""
        config = get_tenant_config()
        self.assertEqual(config.tenant_id, 'pools')

    def test_pool_sizes_not_empty(self):
        """Pool sizes should be populated."""
        config = get_tenant_config()
        sizes = config.get_pool_sizes()
        self.assertGreater(len(sizes), 0)
        # Check that classic size exists
        size_ids = [s['id'] for s in sizes]
        self.assertIn('classic', size_ids)

    def test_prompts_module_has_required_functions(self):
        """Prompts module should have all required functions."""
        prompts = get_tenant_prompts()
        self.assertTrue(hasattr(prompts, 'get_cleanup_prompt'))
        self.assertTrue(hasattr(prompts, 'get_pool_shell_prompt'))
        self.assertTrue(hasattr(prompts, 'get_deck_prompt'))
        self.assertTrue(hasattr(prompts, 'get_quality_check_prompt'))

    def test_unknown_tenant_raises_error(self):
        """Unknown tenant ID should raise ValueError."""
        with self.assertRaises(ValueError):
            get_tenant_config('nonexistent')


class PoolsPromptTest(TestCase):
    """Test pools tenant prompts generate valid content."""

    def test_cleanup_prompt_exists(self):
        """Cleanup prompt should be non-empty."""
        prompts = get_tenant_prompts()
        prompt = prompts.get_cleanup_prompt()
        self.assertIsNotNone(prompt)
        self.assertGreater(len(prompt), 100)
        self.assertIn('backyard', prompt.lower())

    def test_pool_shell_prompt_uses_selections(self):
        """Pool shell prompt should incorporate selections."""
        prompts = get_tenant_prompts()
        selections = {
            'size': 'classic',
            'shape': 'rectangle',
            'finish': 'pebble_blue'
        }
        prompt = prompts.get_pool_shell_prompt(selections)
        self.assertIsNotNone(prompt)
        self.assertIn('pool', prompt.lower())

    def test_deck_prompt_uses_material(self):
        """Deck prompt should incorporate material selection."""
        prompts = get_tenant_prompts()
        selections = {
            'deck_material': 'travertine',
            'deck_color': 'cream'
        }
        prompt = prompts.get_deck_prompt(selections)
        self.assertIsNotNone(prompt)
        self.assertIn('deck', prompt.lower())

    def test_quality_check_prompt_has_scoring(self):
        """Quality check prompt should include scoring criteria."""
        prompts = get_tenant_prompts()
        prompt = prompts.get_quality_check_prompt()
        self.assertIsNotNone(prompt)
        self.assertIn('score', prompt.lower())
        self.assertIn('json', prompt.lower())
