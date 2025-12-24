#!/usr/bin/env python3
"""
Comprehensive Windows Visualizer Quality Testing
Tests window types, door types, and patio enclosures systematically.
"""
import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000/api"
TEST_IMAGES_DIR = Path(__file__).parent
RESULTS_DIR = TEST_IMAGES_DIR / "comprehensive_results"
RESULTS_DIR.mkdir(exist_ok=True)

# Test image selection (use 3 representative images)
TEST_IMAGES = [
    "window_house_01.jpg",
    "window_house_07.jpg",
    "window_house_15.jpg",
]

# Test Configurations - Priority Order
TEST_CONFIGS = {
    # Priority 1: Most Popular Combinations (5 configs)
    "P1-01": {
        "name": "Double Hung Vinyl White - Replace",
        "scope": {
            "project_type": "replace_existing",
            "window_type": "double_hung",
            "frame_material": "vinyl",
            "frame_color": "white",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "none",
            "patio_enclosure_type": "none",
        }
    },
    "P1-02": {
        "name": "Sliding Glass Door with Windows",
        "scope": {
            "project_type": "replace_existing",
            "window_type": "picture",
            "frame_material": "vinyl",
            "frame_color": "white",
            "grille_pattern": "none",
            "glass_option": "low_e",
            "door_type": "sliding_glass",
            "patio_enclosure_type": "none",
        }
    },
    "P1-03": {
        "name": "French Doors Colonial Style",
        "scope": {
            "project_type": "replace_existing",
            "window_type": "casement",
            "frame_material": "wood",
            "frame_color": "white",
            "grille_pattern": "colonial",
            "glass_option": "clear",
            "door_type": "french",
            "patio_enclosure_type": "none",
        }
    },
    "P1-04": {
        "name": "Four-Season Sunroom",
        "scope": {
            "project_type": "enclose_patio",
            "window_type": "slider",
            "frame_material": "vinyl",
            "frame_color": "tan",
            "grille_pattern": "none",
            "glass_option": "low_e",
            "door_type": "sliding_glass",
            "patio_enclosure_type": "four_season",
        }
    },
    "P1-05": {
        "name": "Accordion Door Modern",
        "scope": {
            "project_type": "replace_existing",
            "window_type": "picture",
            "frame_material": "aluminum",
            "frame_color": "black",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "accordion",
            "patio_enclosure_type": "none",
        }
    },

    # Priority 2: Premium and Alternative Options (4 configs)
    "P2-01": {
        "name": "Three-Season Sunroom",
        "scope": {
            "project_type": "enclose_patio",
            "window_type": "slider",
            "frame_material": "vinyl",
            "frame_color": "white",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "sliding_glass",
            "patio_enclosure_type": "three_season",
        }
    },
    "P2-02": {
        "name": "Casement Windows Fiberglass",
        "scope": {
            "project_type": "replace_existing",
            "window_type": "casement",
            "frame_material": "fiberglass",
            "frame_color": "brown",
            "grille_pattern": "prairie",
            "glass_option": "low_e",
            "door_type": "none",
            "patio_enclosure_type": "none",
        }
    },
    "P2-03": {
        "name": "Bi-Fold Door Setup",
        "scope": {
            "project_type": "new_opening",
            "window_type": "picture",
            "frame_material": "aluminum",
            "frame_color": "bronze",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "bifold",
            "patio_enclosure_type": "none",
        }
    },
    "P2-04": {
        "name": "Screen Room Enclosure",
        "scope": {
            "project_type": "enclose_patio",
            "window_type": "slider",
            "frame_material": "aluminum",
            "frame_color": "white",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "sliding_glass",
            "patio_enclosure_type": "screen_room",
        }
    },
}


def get_auth_token():
    """Get authentication token."""
    # Try to get existing token or create test user
    try:
        response = requests.post(f"{API_BASE}/auth/login/", json={
            "username": "testuser",
            "password": "testpass123"
        })
        if response.status_code == 200:
            return response.json().get("access")
    except:
        pass

    # Create test user if needed
    try:
        requests.post(f"{API_BASE}/auth/register/", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        })
        response = requests.post(f"{API_BASE}/auth/login/", json={
            "username": "testuser",
            "password": "testpass123"
        })
        if response.status_code == 200:
            return response.json().get("access")
    except:
        pass

    return None


def submit_visualization(image_path, scope, token):
    """Submit a visualization request and wait for completion."""
    headers = {"Authorization": f"Bearer {token}"}

    with open(image_path, "rb") as f:
        files = {"original_image": f}
        data = {
            "tenant_id": "windows",
            "scope": json.dumps(scope)
        }

        response = requests.post(
            f"{API_BASE}/visualizations/",
            headers=headers,
            files=files,
            data=data
        )

    if response.status_code != 201:
        return None, f"Failed to submit: {response.status_code}"

    viz_id = response.json().get("id")

    # Poll for completion
    max_wait = 180  # 3 minutes max
    start = time.time()

    while time.time() - start < max_wait:
        response = requests.get(
            f"{API_BASE}/visualizations/{viz_id}/",
            headers=headers
        )

        if response.status_code != 200:
            return None, f"Failed to check status: {response.status_code}"

        data = response.json()
        status = data.get("status")

        if status == "complete":
            return data, None
        elif status == "failed":
            return None, data.get("error_message", "Unknown error")

        time.sleep(5)

    return None, "Timeout waiting for completion"


def run_test(test_id, config, image_path, token):
    """Run a single test configuration."""
    print(f"  Testing with {image_path.name}...")

    start_time = time.time()
    result, error = submit_visualization(image_path, config["scope"], token)
    elapsed = time.time() - start_time

    if error:
        return {
            "test_id": test_id,
            "config_name": config["name"],
            "image": image_path.name,
            "status": "error",
            "error": error,
            "duration_seconds": elapsed
        }

    # Extract quality score from response
    quality_score = None
    if result.get("results"):
        metadata = result["results"][0].get("metadata", {})
        quality_score = metadata.get("quality_score")

    return {
        "test_id": test_id,
        "config_name": config["name"],
        "image": image_path.name,
        "status": "success",
        "quality_score": quality_score,
        "duration_seconds": elapsed,
        "result_id": result.get("id"),
        "result_image": result["results"][0].get("generated_image_url") if result.get("results") else None
    }


def run_all_tests(test_filter=None):
    """Run all tests or filtered subset."""
    print("=" * 60)
    print("COMPREHENSIVE WINDOWS VISUALIZER QUALITY TEST")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # Get auth token
    print("\nAuthenticating...")
    token = get_auth_token()
    if not token:
        print("ERROR: Failed to authenticate")
        return
    print("Authenticated successfully")

    # Filter tests if specified
    tests_to_run = TEST_CONFIGS
    if test_filter:
        tests_to_run = {k: v for k, v in TEST_CONFIGS.items() if k.startswith(test_filter)}

    print(f"\nRunning {len(tests_to_run)} test configurations x {len(TEST_IMAGES)} images")
    print(f"Total tests: {len(tests_to_run) * len(TEST_IMAGES)}")
    print("-" * 60)

    all_results = []

    for test_id, config in tests_to_run.items():
        print(f"\n[{test_id}] {config['name']}")

        for image_name in TEST_IMAGES:
            image_path = TEST_IMAGES_DIR / image_name
            if not image_path.exists():
                print(f"  WARNING: Image not found: {image_name}")
                continue

            result = run_test(test_id, config, image_path, token)
            all_results.append(result)

            if result["status"] == "success":
                score = result.get("quality_score", "N/A")
                print(f"    OK - Quality: {score} ({result['duration_seconds']:.1f}s)")
            else:
                print(f"    FAIL - {result.get('error', 'Unknown error')}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = RESULTS_DIR / f"results_{timestamp}.json"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(all_results),
        "successful": len([r for r in all_results if r["status"] == "success"]),
        "failed": len([r for r in all_results if r["status"] == "error"]),
        "results": all_results
    }

    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total: {summary['total_tests']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    if summary['total_tests'] > 0:
        success_rate = (summary['successful'] / summary['total_tests']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    print(f"Results saved to: {results_file}")

    # Calculate average quality scores per category
    if summary['successful'] > 0:
        print("\nQuality Scores by Category:")
        categories = {}
        for r in all_results:
            if r["status"] == "success" and r.get("quality_score"):
                category = r["test_id"].split("-")[0]
                if category not in categories:
                    categories[category] = []
                categories[category].append(r["quality_score"])

        for cat, scores in sorted(categories.items()):
            avg = sum(scores) / len(scores)
            print(f"  {cat}: {avg:.2f} avg ({len(scores)} tests)")

    return summary


if __name__ == "__main__":
    # Check for filter argument
    test_filter = None
    if len(sys.argv) > 1:
        test_filter = sys.argv[1]
        print(f"Filter: {test_filter}")

    run_all_tests(test_filter)
