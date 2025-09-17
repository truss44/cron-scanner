#!/bin/bash

# Exit on error
set -e

# Set the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
USE_VENV=true

# Function to print usage information
print_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help      Show this help message and exit"
    echo "  -i, --install   Install dependencies and exit"
    echo "  -r, --run       Run the cron scanner (default)"
    echo "  -u, --uninstall Remove the virtual environment"
    echo "  --args ARGS     Additional arguments to pass to the cron scanner"
    echo "                  Examples:"
    echo "                    --args='--time-span 1d'"
    echo "                    --args='--start-time 2025-01-01 --end-time 2025-01-07'"
    echo "                    --args='--format json --output output.json'"
    echo "\nBy default, output is written to a timestamped file in the current directory (CSV unless --format is specified)."
}

# Function to create and activate virtual environment (with fallback if venv unavailable)
setup_venv() {
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is required but not installed." >&2
        exit 1
    fi

    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        if python3 -m venv "$VENV_DIR"; then
            # Activate the virtual environment
            # shellcheck disable=SC1090
            source "$VENV_DIR/bin/activate"
            
            # Upgrade pip
            echo "Upgrading pip..."
            pip install --upgrade pip
            
            echo "Virtual environment setup complete."
        else
            echo "Warning: Could not create a virtual environment (python3-venv may be missing)." >&2
            echo "Falling back to user-level installation without a virtual environment." >&2
            USE_VENV=false
            # Try to ensure pip exists and is recent
            if ! python3 -m pip --version >/dev/null 2>&1; then
                echo "pip is not available for Python 3. Please install it (e.g., apt install python3-pip) and re-run." >&2
                exit 1
            fi
            python3 -m pip install --user --upgrade pip
        fi
    else
        # Activate the virtual environment
        if [ -f "$VENV_DIR/bin/activate" ]; then
            # shellcheck disable=SC1090
            source "$VENV_DIR/bin/activate"
            # Verify venv has working pip, otherwise fall back
            if ! "$VENV_DIR/bin/python" -m pip --version >/dev/null 2>&1; then
                echo "Virtual environment appears broken. Falling back to user-level installs." >&2
                USE_VENV=false
            fi
        else
            USE_VENV=false
        fi
    fi
}

# Ensure requirements are installed in the active environment
install_reqs() {
    if [ "$USE_VENV" = true ]; then
        echo "Installing requirements into virtual environment..."
        "$VENV_DIR/bin/python" -m pip install -r "$PROJECT_DIR/requirements.txt"
    else
        echo "Installing requirements into user site-packages..."
        if python3 -m pip --version >/dev/null 2>&1; then
            python3 -m pip install --user -r "$PROJECT_DIR/requirements.txt"
        else
            echo "pip not found for Python 3. Attempting to bootstrap via ensurepip..." >&2
            if python3 -m ensurepip --upgrade >/dev/null 2>&1; then
                python3 -m pip install --user -r "$PROJECT_DIR/requirements.txt"
            else
                echo "Failed to bootstrap pip automatically." >&2
                echo "Please install pip or the Python venv module and re-run:" >&2
                echo "  - Debian/Ubuntu: sudo apt install python3-pip    (or: sudo apt install python3-venv)" >&2
                echo "  - Fedora: sudo dnf install python3-pip" >&2
                echo "  - Arch: sudo pacman -S python-pip" >&2
                exit 1
            fi
        fi
        # Ensure user site is discoverable
        USER_SITE=$(python3 -m site --user-site 2>/dev/null || true)
        if [ -n "$USER_SITE" ]; then
            export PYTHONPATH="${USER_SITE}:${PYTHONPATH}"
        fi
    fi
}

# Function to run the cron scanner
run_scanner() {
    # Activate the virtual environment
    if [ "$USE_VENV" = true ] && [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    fi
    
    # Ensure we run from the project directory so the package is importable
    cd "$PROJECT_DIR"

    # Run the cron scanner with any additional arguments
    if [ "$USE_VENV" = true ]; then
        python -m cron_scanner.scanner "$@"
    else
        # Ensure user site-packages are discoverable
        USER_SITE=$(python3 -m site --user-site 2>/dev/null || true)
        if [ -n "$USER_SITE" ]; then
            export PYTHONPATH="${USER_SITE}:${PYTHONPATH}"
        fi
        python3 -m cron_scanner.scanner "$@"
    fi
}

# Function to clean up the virtual environment
cleanup_venv() {
    if [ -d "$VENV_DIR" ]; then
        echo "Removing virtual environment..."
        rm -rf "$VENV_DIR"
        echo "Virtual environment removed."
    else
        echo "Virtual environment not found. Nothing to remove."
    fi
    exit 0
}

# Parse command-line arguments
INSTALL_ONLY=false
RUN_SCANNER=true
EXTRA_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            print_usage
            exit 0
            ;;
        -i|--install)
            INSTALL_ONLY=true
            RUN_SCANNER=false
            shift
            ;;
        -r|--run)
            RUN_SCANNER=true
            shift
            ;;
        -u|--uninstall)
            cleanup_venv
            ;;
        --args)
            shift
            EXTRA_ARGS="$1"
            shift
            ;;
        --args=*)
            EXTRA_ARGS="${1#*=}"
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            print_usage >&2
            exit 1
            ;;
    esac
done

# Main execution
if [ "$INSTALL_ONLY" = true ]; then
    setup_venv
    install_reqs
    echo "Installation complete. Run '$0' to start the cron scanner."
elif [ "$RUN_SCANNER" = true ]; then
    setup_venv
    install_reqs
    run_scanner $EXTRA_ARGS
fi

exit 0
