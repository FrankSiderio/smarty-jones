# Publishing smarty-jones to PyPI

This document outlines the steps to publish the smarty-jones package to PyPI.

## Prerequisites & Account Setup

### 1. Create PyPI Accounts
- **PyPI (production)**: Create account at [pypi.org](https://pypi.org/account/register/)  
- **TestPyPI (testing)**: Create account at [test.pypi.org](https://test.pypi.org/account/register/)

### 2. Enable Two-Factor Authentication
- Enable 2FA on both accounts for security
- You'll need an authenticator app like Google Authenticator

### 3. Create API Tokens
- Go to Account Settings → API Tokens
- Create tokens for both PyPI and TestPyPI
- Store these securely (you'll need them for publishing)

## Publishing with the Automated Script

### 4. Update Version Number
- Update the version in `pyproject.toml` for new releases
- Follow semantic versioning (MAJOR.MINOR.PATCH)

### 5. Run the Publishing Script
```bash
./scripts/publish.sh
```

The script will:
- ✅ Check and install required tools (`build`, `twine`)
- ✅ Warn about uncommitted changes
- ✅ Clean previous builds
- ✅ Build the package (wheel + source distribution)
- ✅ Validate the build
- ✅ Prompt you to choose: TestPyPI, PyPI, or both
- ✅ Handle uploads with proper authentication prompts
- ✅ Provide installation commands and links
- ✅ Suggest git tagging commands

### 6. Authentication
When prompted during upload:
- **Username**: `__token__`
- **Password**: Your PyPI/TestPyPI API token

### 7. Verify Publication
- **TestPyPI**: `https://test.pypi.org/project/smarty-jones/`
- **PyPI**: `https://pypi.org/project/smarty-jones/`

## Manual Publishing (Alternative)

If you prefer manual control, you can run the commands individually:

```bash
# Clean and build
rm -rf dist/ build/ *.egg-info/
python -m build
python -m twine check dist/*

# Upload to TestPyPI
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Upload to PyPI  
python -m twine upload dist/*
```

## Post-Publication

### 8. Tag the Release (Git)
```bash
git tag v0.1.0  # Replace with your version
git push origin v0.1.0
```

### 9. Create GitHub Release
- Go to your GitHub repository
- Create a new release with the version tag
- Add release notes describing changes

## Troubleshooting

### Common Issues
- **Package name already taken**: Choose a different name in `pyproject.toml`
- **Authentication failed**: Verify your API tokens are correct
- **Build errors**: Check dependencies and Python version compatibility
- **Upload failed**: Ensure you're using the correct repository URL
- **Script permission denied**: Run `chmod +x scripts/publish.sh`

## Future Automation

Consider setting up GitHub Actions for automated publishing:
1. Create `.github/workflows/publish.yml`
2. Configure PyPI API tokens as GitHub secrets
3. Auto-publish on new releases/tags

## Quick Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `README.md` if needed
- [ ] Commit and push changes to git
- [ ] Run `./scripts/publish.sh`
- [ ] Choose TestPyPI for testing (recommended first)
- [ ] Test install: `pip install --index-url https://test.pypi.org/simple/ smarty-jones`
- [ ] Run script again and choose PyPI for production release
- [ ] Verify on PyPI: `https://pypi.org/project/smarty-jones/`
- [ ] Tag release: `git tag v{version} && git push origin v{version}`
- [ ] Create GitHub release