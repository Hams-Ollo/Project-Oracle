# Git Branching Strategy

## Overview

Project Oracle follows a trunk-based development strategy with feature branches. This document outlines our branching structure and workflow procedures.

## Branch Structure

### Main Branches

#### `main`

- Production-ready code
- Protected branch
- Requires pull request and review
- Auto-deploys to production
- Tagged for releases

#### `develop`

- Integration branch
- Latest development code
- Auto-deploys to staging
- Continuous integration testing

### Supporting Branches

#### Feature Branches

- **Naming**: `feature/description-of-feature`
- **Example**: `feature/add-research-agent`
- Created from: `develop`
- Merge back to: `develop`
- Delete after merge

#### Bugfix Branches

- **Naming**: `bugfix/description-of-bug`
- **Example**: `bugfix/fix-context-retrieval`
- Created from: `develop`
- Merge back to: `develop`
- Delete after merge

#### Hotfix Branches

- **Naming**: `hotfix/description-of-fix`
- **Example**: `hotfix/api-key-validation`
- Created from: `main`
- Merge back to: `main` and `develop`
- For urgent production fixes

#### Release Branches

- **Naming**: `release/version-number`
- **Example**: `release/v1.0.0`
- Created from: `develop`
- Merge back to: `main` and `develop`
- For release preparation

## Workflow Guidelines

### Feature Development

1. Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

2. Development Work

```bash
# Make changes
git add .
git commit -m "feat(scope): description"
```

3. Stay Updated

```bash
git checkout develop
git pull origin develop
git checkout feature/your-feature-name
git rebase develop
```

4. Push Changes

```bash
git push origin feature/your-feature-name
```

### Code Review Process

1. Pull Request Creation
   - Create PR against `develop`
   - Fill out PR template
   - Link related issues
   - Request reviewers

2. Review Requirements
   - Passing CI/CD checks
   - Code review approval
   - Documentation updates
   - Test coverage maintained

### Release Process

1. Create Release Branch

```bash
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0
```

2. Version Updates

```bash
# Update version numbers
# Update CHANGELOG.md
git commit -m "chore(release): prepare v1.0.0"
```

3. Finalize Release

```bash
git checkout main
git merge release/v1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main --tags
```

## Branch Protection Rules

### Main Branch (`main`)

- Require pull request reviews
- Require status checks
- No direct pushes
- No force pushes
- Maintain linear history

### Development Branch (`develop`)

- Require pull request reviews
- Require status checks
- No direct pushes
- Allow force pushes with lease

## Best Practices

### Commit Messages

```bash
# Format
<type>(<scope>): <description>

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Formatting
refactor: Code restructuring
test:     Adding tests
chore:    Maintenance
```

### Branch Management

1. Regular Cleanup

```bash
# Delete merged local branches
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d
```

2. Remote Cleanup

```bash
# Delete merged remote branches
git push origin --delete feature/completed-feature
```

### Conflict Resolution

1. Local Conflicts

```bash
git checkout develop
git pull origin develop
git checkout feature/your-feature
git rebase develop
# Resolve conflicts
git rebase --continue
```

2. Remote Conflicts

```bash
git fetch origin
git rebase origin/develop
# Resolve conflicts
git push origin feature/your-feature --force-with-lease
```

## Tools and Integration

### Git Hooks

```bash
# Pre-commit hook example
#!/bin/sh
python -m pytest
if [ $? -ne 0 ]; then
    echo "Tests must pass before commit!"
    exit 1
fi
```

### CI/CD Integration

- Automated tests on PR
- Linting checks
- Documentation builds
- Security scanning
