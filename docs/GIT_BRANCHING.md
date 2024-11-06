# Git Branching Strategy

## Branch Structure

### Main Branches

- `main` - Production-ready code
- `develop` - Integration branch for features

### Supporting Branches

- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes
- `release/*` - Release preparation

## Workflow

### Feature Development

1. Create from: `develop`
2. Name format: `feature/description-of-feature`
3. Merge back to: `develop`
