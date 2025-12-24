# Maintenance Audit - December 24, 2025

## Summary

Comprehensive codebase maintenance audit completed. Found issues ranging from critical (test failures) to minor (outdated deps).

---

## Findings by Priority

### CRITICAL (Fix Immediately)

#### 1. Test Suite Failures (7 issues)
- **4 test failures** - Tests out of sync with current code
- **3 import errors** - Tests import removed modules (`ScreenType`, `screen_visualizer`)

| Test File | Issue |
|-----------|-------|
| `test_ai_services.py` | ImportError: `ScreenType` removed from models |
| `test_visualizer_comprehensive.py` | ImportError: `screen_visualizer` module gone |
| `test_tenant_registry.py` | AttributeError: `get_pool_sizes` method doesn't exist |
| `test_tenant_api.py` | Missing `tenant_id` in config response |
| `test_screen_visualizer.py` (x3) | Gemini call count assertions wrong |

**Risk:** HIGH - Broken tests mean no safety net for changes
**Action:** Fix or delete broken tests before any new development

---

### HIGH (Fix This Session)

#### 2. __pycache__ Cleanup
- **11 directories** with stale bytecode outside venv
- **43 .pyc files** cluttering the repo

**Action:** Run cleanup command:
```bash
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -not -path "./venv/*" -delete 2>/dev/null
```

#### 3. Missing Dependency at Runtime
- `python-dotenv` not in requirements.txt but needed
- Django check failed until installed

**Action:** Add to requirements.txt:
```
python-dotenv>=1.0.0
```

---

### MEDIUM (Fix This Week)

#### 4. Media Folder Size (968MB)
| Folder | Size | Action |
|--------|------|--------|
| `originals/` | 758MB | Already gitignored, OK |
| `pipeline_steps/` | 102MB | Consider periodic cleanup |
| `generated/` | 83MB | Already gitignored, OK |
| `pdfs/` | 25MB | Already gitignored, OK |
| `thinking_logs/` | 124KB | 30 files, OK |

**Action:** No immediate action needed, folders are gitignored

#### 5. Outdated Dependencies
**Python (3 packages):**
- boto3: 1.42.15 → 1.42.16 (patch)
- botocore: 1.42.15 → 1.42.16 (patch)
- pip: 24.0 → 25.3 (major)

**npm (18 packages):**
| Package | Current | Latest | Risk |
|---------|---------|--------|------|
| react/react-dom | 19.1.0 | 19.2.3 | LOW |
| axios | 1.8.4 | 1.13.2 | MEDIUM |
| cypress | 14.4.0 | 15.8.1 | HIGH (major) |
| zustand | 5.0.3 | 5.0.9 | LOW |

**Action:** Update patch versions now; schedule major versions for separate PR

#### 6. TODOs in Code (9 items)
| File | Line | TODO |
|------|------|------|
| settings.py | 102 | Switch to PostgreSQL |
| registry.py | 225 | Implement provider selection |
| gemini_provider.py | 167 | Implement enhancement |
| views.py | 172 | Trigger AI processing |
| views.py | 441 | Add auth views |
| calculators/__init__.py | 14-17 | Phase 2 calculators |

**Action:** Review and convert to issues or delete stale TODOs

---

### LOW (When Time Permits)

#### 7. Log File Management
- Logs are small (1070 lines total) - good
- Token refresh warnings recurring (Dec 22)

**Action:** No cleanup needed, but investigate token refresh issue

#### 8. Git Status
- 12 deleted thinking logs (cleanup from last session)
- 2 untracked temp files (`12.23.txt`, `12.txt`)
- 1 commit ahead of origin

**Action:**
```bash
git checkout -- media/thinking_logs/  # restore or
git add -A && git commit -m "chore: cleanup stale files"
git push origin master
```

#### 9. Hardcoded Test Credentials
Found in test files (acceptable for tests):
- `password='password123'` in auth_views.py:105
- `api_key="fake_key"` in test files

**Action:** No change needed - these are test fixtures

---

## Health Check Results

| Check | Status |
|-------|--------|
| Django system check | PASS (0 issues) |
| Tenants registered | PASS (pools, windows, roofs, screens) |
| .gitignore | PRESENT and comprehensive |
| .env file | EXISTS (4 vars, properly gitignored) |
| Database | SQLITE (388KB) |
| Secrets scan | CLEAN (no leaked credentials) |

---

## Recommended Execution Order

### Batch 1: Critical Fixes (20 min)
1. [ ] Clean __pycache__ directories
2. [ ] Add python-dotenv to requirements.txt
3. [ ] Delete or fix broken test files

### Batch 2: Test Suite Fix (30 min)
4. [ ] Update test_tenant_api.py assertions
5. [ ] Update test_screen_visualizer.py call counts
6. [ ] Delete obsolete test_ai_services.py
7. [ ] Delete obsolete test_visualizer_comprehensive.py

### Batch 3: Dependencies (15 min)
8. [ ] Update boto3, botocore (pip)
9. [ ] Update react, axios, zustand (npm)
10. [ ] Run tests to verify

### Batch 4: Git Cleanup (5 min)
11. [ ] Remove temp files
12. [ ] Commit and push

---

## Do NOT Do (Out of Scope)

- Major Cypress upgrade (15.x) - breaking changes, separate PR
- Switch to PostgreSQL - architectural change
- Implement Phase 2 calculators - feature work
- Fix PDF generation - requires investigation

---

## Session Notes

**Date:** 2025-12-24
**Duration:** ~45 min audit
**Tools Used:** Django check, pip/npm outdated, grep, find

### Errors Found in Logs

1. **Token refresh failures** (Dec 22) - 30+ warnings about expired tokens
   - Not blocking, but indicates session handling issue

2. **Gemini API key leak** (Dec 13) - Historical, key was replaced
   - Old error, no current exposure

### Next Session Should

1. Execute Batch 1-4 above
2. Investigate token refresh issue
3. Update TODO.md with resolved items
