#!/bin/bash
set -e  # Exit on any error

echo "🚀 Publishing smarty-jones to PyPI"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to prompt for confirmation
confirm() {
    read -p "$1 (y/n): " choice
    case "$choice" in 
        y|Y ) return 0;;
        n|N ) echo "Aborted."; exit 1;;
        * ) echo "Invalid choice. Aborted."; exit 1;;
    esac
}

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}Warning: No virtual environment detected. Activating .venv...${NC}"
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo -e "${RED}Error: .venv directory not found. Please create and activate a virtual environment.${NC}"
        exit 1
    fi
fi

# Ensure required tools are installed
echo "📦 Checking required tools..."
python -c "import build, twine" 2>/dev/null || {
    echo -e "${YELLOW}Installing build and twine...${NC}"
    pip install --upgrade build twine
}

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}Warning: You have uncommitted changes.${NC}"
    confirm "Continue anyway?"
fi

# Get current version
VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
echo "📋 Current version: $VERSION"

# Ask which repository to publish to
echo ""
echo "Choose publishing target:"
echo "1) TestPyPI (for testing)"
echo "2) Production PyPI"
echo "3) Both (TestPyPI first, then PyPI)"
read -p "Enter choice (1-3): " repo_choice

case $repo_choice in
    1) REPOS=("test");;
    2) REPOS=("pypi");;
    3) REPOS=("test" "pypi");;
    *) echo "Invalid choice. Exited."; exit 1;;
esac

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build package
echo "🔨 Building package..."
python -m build

# Check package
echo "✅ Checking package..."
python -m twine check dist/*

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Package check failed. Please fix errors before publishing.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Package built and validated successfully!${NC}"
echo ""

# Publish to selected repositories
for repo in "${REPOS[@]}"; do
    if [ "$repo" = "test" ]; then
        echo "📤 Uploading to TestPyPI..."
        echo "Use username: __token__"
        echo "Use your TestPyPI API token as password"
        python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Successfully uploaded to TestPyPI!${NC}"
            echo "Test installation with:"
            echo "pip install --index-url https://test.pypi.org/simple/ smarty-jones==$VERSION"
            echo ""
            
            if [[ " ${REPOS[@]} " =~ " pypi " ]]; then
                confirm "TestPyPI upload successful. Continue with PyPI upload?"
            fi
        else
            echo -e "${RED}❌ TestPyPI upload failed.${NC}"
            exit 1
        fi
        
    elif [ "$repo" = "pypi" ]; then
        echo "📤 Uploading to Production PyPI..."
        echo "Use username: __token__"
        echo "Use your PyPI API token as password"
        python -m twine upload dist/*
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Successfully uploaded to PyPI!${NC}"
            echo "Your package is now available at:"
            echo "https://pypi.org/project/smarty-jones/"
            echo ""
            echo "Install with: pip install smarty-jones==$VERSION"
        else
            echo -e "${RED}❌ PyPI upload failed.${NC}"
            exit 1
        fi
    fi
done

# Auto-tag the release
echo ""
TAG="v$VERSION"
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Tag $TAG already exists.${NC}"
else
    echo "🏷️  Creating git tag: $TAG"
    if confirm "Create and push tag $TAG?"; then
        git tag "$TAG"
        git push origin "$TAG"
        echo -e "${GREEN}✅ Tagged and pushed $TAG${NC}"
        echo ""
        echo "📋 Create GitHub release at:"
        echo "https://github.com/FrankSiderio/smarty-jones/releases/new?tag=$TAG"
    else
        echo "Skipped tagging."
    fi
fi

echo ""
echo -e "${GREEN}🎉 Publishing complete!${NC}"