# Git Quick Reference Guide

## Daily Git Commands

### Basic Workflow
```bash
# Check status of your files
git status

# Add files to staging
git add filename           # Add specific file
git add .                 # Add all files

# Commit your changes
git commit -m "Your message describing the changes"

# Push changes to GitHub
git push
```

### Viewing Changes
```bash
# See changes in files
git diff                  # Show unstaged changes
git diff --staged         # Show staged changes

# View commit history
git log                   # Show commit history
git log --oneline        # Compact view of history
```

### Working with Branches
```bash
# Branch operations
git branch               # List branches
git branch name          # Create new branch
git checkout name        # Switch to branch
git checkout -b name     # Create and switch to new branch

# Merge branches
git merge branchname     # Merge branch into current branch
```

### Syncing with GitHub
```bash
# Get latest changes
git pull                 # Update your local repository

# Push your changes
git push                 # Send commits to GitHub
git push -u origin main  # First time push to main branch
```

## Common Scenarios

### Starting New Work
1. Get latest changes:
```bash
git pull
```

2. Create new branch:
```bash
git checkout -b feature-name
```

3. Make your changes and commit:
```bash
git add .
git commit -m "Description of changes"
```

4. Push to GitHub:
```bash
git push -u origin feature-name
```

### Updating Your Repository
1. Check current status:
```bash
git status
```

2. Add and commit changes:
```bash
git add .
git commit -m "Update description"
```

3. Push to GitHub:
```bash
git push
```

### Fixing Mistakes
```bash
# Undo changes in a file
git checkout -- filename

# Undo last commit (keep changes)
git reset --soft HEAD^

# Discard all local changes
git reset --hard HEAD
```

## Best Practices

1. **Commit Messages**
   - Use clear, descriptive messages
   - Start with a verb (Add, Update, Fix, etc.)
   - Keep it concise but informative

2. **Branching**
   - Keep main/master branch clean
   - Create branches for new features
   - Delete branches after merging

3. **Before Pushing**
   - Review your changes (git status)
   - Test your code
   - Make sure commits are logical

4. **Regular Updates**
   - Pull regularly to stay up to date
   - Resolve conflicts promptly
   - Keep commits small and focused

## Getting Help
```bash
git help command         # Detailed help for command
git command --help      # Same as above
```

Remember: You can always check `git status` to see what's going on in your repository. It's a safe command that won't change anything.
