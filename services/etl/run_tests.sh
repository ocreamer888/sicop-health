#!/bin/bash

# SICOP ETL Test Runner
# Usage: ./run_tests.sh [options]
# Options:
#   -u, --unit       Run only unit tests
#   -i, --integration Run only integration tests
#   -c, --coverage   Run with coverage report
#   -v, --verbose    Verbose output

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
TEST_PATH="tests/"
PYTEST_OPTS="-v"
MARKER=""
COVERAGE=""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  SICOP ETL Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--unit)
            MARKER="-m 'unit'"
            echo -e "${YELLOW}Running: Unit tests only${NC}"
            shift
            ;;
        -i|--integration)
            MARKER="-m 'integration'"
            echo -e "${YELLOW}Running: Integration tests only${NC}"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=. --cov-report=html --cov-report=term-missing"
            echo -e "${YELLOW}Running: With coverage report${NC}"
            shift
            ;;
        -v|--verbose)
            PYTEST_OPTS="-vv --tb=long"
            shift
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  -u, --unit         Run only unit tests"
            echo "  -i, --integration  Run only integration tests"
            echo "  -c, --coverage     Run with coverage report"
            echo "  -v, --verbose      Verbose output"
            echo "  -h, --help         Show this help"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh              # Run all tests"
            echo "  ./run_tests.sh -u           # Run unit tests only"
            echo "  ./run_tests.sh -c           # Run all tests with coverage"
            echo "  ./run_tests.sh -u -c        # Run unit tests with coverage"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Run './run_tests.sh -h' for help"
            exit 1
            ;;
    esac
done

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV}" && -d "venv" ]]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Run tests
echo ""
echo -e "${BLUE}Running pytest...${NC}"
echo ""

cmd="python -m pytest ${TEST_PATH} ${PYTEST_OPTS} ${COVERAGE} ${MARKER}"
echo -e "${BLUE}Command: ${cmd}${NC}"
echo ""

if eval $cmd; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  All tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    if [[ -n "$COVERAGE" ]]; then
        echo ""
        echo -e "${BLUE}Coverage report generated in: htmlcov/index.html${NC}"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  Tests failed!${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
