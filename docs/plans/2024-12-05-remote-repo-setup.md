# Remote Repository Setup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a GitHub remote repository and push the local 'teach_paper' repository to it.

**Architecture:** Use GitHub CLI (gh) to create the repository remotely, then configure the local git repository to use the remote origin and push all commits.

**Tech Stack:** Git, GitHub CLI

---

### Task 1: Install and Verify GitHub CLI

**Files:**
- Test: command line verification

**Step 1: Verify GitHub CLI is installed**

```bash
gh --version
```
Expected: Version number if installed, error if not

**Step 2: If not installed, install GitHub CLI**

```bash
# For Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

**Step 3: Verify installation**

```bash
gh --version
```
Expected: Shows GitHub CLI version

**Step 4: Login to GitHub**

```bash
gh auth login
```
- Choose GitHub.com
- Select "Login with a web browser"
- Follow the authentication flow

**Step 5: Verify authentication**

```bash
gh auth status
```
Expected: Shows logged in user and authentication status

**Step 6: Commit**

```bash
git add .
git commit -m "chore: verify GitHub CLI installation and authentication"
```

---

### Task 2: Create Remote GitHub Repository

**Files:**
- Test: Verify repository creation

**Step 1: Create repository using GitHub CLI**

```bash
gh repo create teach_paper --public --source=. --remote=origin --push
```
Expected: Shows repository URL and confirms creation

**Step 2: Verify remote was added**

```bash
git remote -v
```
Expected: Shows origin URL with GitHub repository

**Step 3: Commit**

```bash
git add .
git commit -m "feat: create remote GitHub repository"
```

---

### Task 3: Push All Local Branches and Tags

**Files:**
- Test: Verify all content is on remote

**Step 1: Push current branch (master)**

```bash
git push -u origin master
```
Expected: Shows commits being pushed and branch setup

**Step 2: Check if any other local branches exist**

```bash
git branch -a
```

**Step 3: Push all other branches if they exist**

```bash
git push --all origin
```

**Step 4: Push all tags**

```bash
git push --tags
```

**Step 5: Verify remote branches**

```bash
git ls-remote origin
```
Expected: Shows all branches and their commit hashes

**Step 6: Commit**

```bash
git add .
git commit -m "feat: push all branches and tags to remote"
```

---

### Task 4: Verify Repository Setup

**Files:**
- Test: Verify repository is accessible and complete

**Step 1: Check repository URL**

```bash
git remote get-url origin
```
Expected: Shows GitHub repository URL

**Step 2: View repository on GitHub**

```bash
gh repo view teach_paper --web
```
Expected: Opens browser showing the repository

**Step 3: Verify local and remote are in sync**

```bash
git status
```
Expected: Shows "Your branch is up to date with 'origin/master'"

**Step 4: Final commit**

```bash
git add .
git commit -m "chore: complete remote repository setup verification"
```

---

Plan complete and saved to `docs/plans/2024-12-05-remote-repo-setup.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**