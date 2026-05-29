# Git Workflow (Solo / Kleinprojekte)

## Branch-Struktur

```text
main        -> stabile Version
dev         -> aktuelle Entwicklung
feature/*   -> neues Feature
bugfix/*    -> Fehlerbehebung
release/*   -> Release-Vorbereitung
```

---

## Neues Projekt

```bash
git init
git branch -M main
git remote add origin <REPOSITORY-URL>
git add .
git commit -m "Initial commit"
git push -u origin main
```

---

## Entwicklungsbranch

```bash
git checkout -b dev
git push -u origin dev
```

---

## Feature

```bash
git checkout dev
git checkout -b feature/neues-feature

git add .
git commit -m "Add new feature"

git checkout dev
git merge feature/neues-feature
git branch -d feature/neues-feature
```

---

## Bugfix

```bash
git checkout dev
git checkout -b bugfix/problembehebung

git add .
git commit -m "Fix issue"

git checkout dev
git merge bugfix/problembehebung
git branch -d bugfix/problembehebung
```

---

## Release

```bash
git checkout dev
git checkout -b release/v1.1.0

git checkout main
git merge release/v1.1.0
git tag v1.1.0

git checkout dev
git merge main
```

---

## Nützliche Befehle

```bash
git status
git diff
git log --oneline
git branch
git pull
git push
```

---

## Änderungen verwerfen

```bash
git restore .
```

---

## Commit bearbeiten

```bash
git commit --amend
```