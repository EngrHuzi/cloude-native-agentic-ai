#!/bin/bash
# Run pytest with coverage reporting

# Default values
PACKAGE_NAME="${1:-.}"
MIN_COVERAGE="${2:-80}"

echo "Running pytest with coverage..."
echo "Package: $PACKAGE_NAME"
echo "Minimum coverage: $MIN_COVERAGE%"
echo ""

# Run pytest with coverage
pytest \
    --cov="$PACKAGE_NAME" \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-fail-under="$MIN_COVERAGE" \
    "$@"

PYTEST_EXIT_CODE=$?

echo ""
if [ $PYTEST_EXIT_CODE -eq 0 ]; then
    echo "✓ Tests passed with sufficient coverage!"
    echo "HTML coverage report: htmlcov/index.html"
else
    echo "✗ Tests failed or coverage below $MIN_COVERAGE%"
fi

exit $PYTEST_EXIT_CODE
