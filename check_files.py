import os

ROOT = r"C:\Users\DELL\OneDrive\Escritorio\SIAAF\sistema-titulacion-unl"
BACKEND = os.path.join(ROOT, "backend")

files = [
    (os.path.join(ROOT, ".gitleaksignore"), "ROOT/.gitleaksignore"),
    (os.path.join(BACKEND, ".bandit"), "BACKEND/.bandit"),
    (os.path.join(ROOT, "docs", "security_report.md"), "ROOT/docs/security_report.md"),
]

for f, label in files:
    exists = os.path.exists(f)
    status = "EXISTS" if exists else "MISSING"
    print(label + ": " + status + " -> " + f)