# Sprint 5 Task List: Dashboard Analytics APIs

- [ ] Define Pydantic schemas in `app/schemas/dashboard.py` (with ChartResponse, datasets, and comparison metrics)
- [ ] Create repository classes in `app/repositories/dashboard.py` implementing database aggregation queries (including previous period counts and the complaints-charger association heuristic)
- [ ] Create service classes in `app/services/dashboard.py` without in-memory caching, computing overview comparisons and mapping database results to standardized chart structures
- [ ] Implement endpoint routes in `app/api/v1/dashboard.py` protecting them with JWT auth
- [ ] Register new router in `app/api/v1/api.py`
- [ ] Write tests in `tests/test_analytics.py` verifying overview metrics, date filters, empty datasets, and recent activities
- [ ] Validate code with `ruff`, `black`, `isort`, `mypy`, and `pytest`
