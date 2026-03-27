# How to run tests
Different type of tests take different amount of time. meta_extractor tests and decompiler_tests are pretty fast. Api tests are slow.

## meta_extractor tests (take around 2s)
docker compose exec meta-extractor-worker sh -c "pip install pytest==8.3.5 pytest-cov==6.1.1 && coverage run --module --data-file=/coverage/.coverage.meta_extractor pytest /daas/tests/"

## Decompiler tests (take around 2s)
docker compose exec pe-worker sh -c "pip install pytest==8.3.5 pytest-cov==6.1.1 && coverage run --module --data-file=/coverage/.coverage.decompilers pytest /daas/tests/"

## Api tests (take around 400s)
docker compose exec api sh -c "coverage run --data-file=/coverage/.coverage.api_tests /daas/manage.py test daas_app.tests.unit_tests -v 1 --force-color --exclude stress_test_csharp --noinput"
