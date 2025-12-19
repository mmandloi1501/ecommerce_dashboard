# -------------------------------
# E-COMMERCE DASHBOARD AUTOMATION
# -------------------------------

# 1️⃣ Set execution policy temporarily (if needed)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 2️⃣ Activate virtual environment
$venvPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..."
    & $venvPath
} else {
    Write-Host "Virtual environment not found. Please create it first."
    exit
}

# 3️⃣ Install required packages
if (Test-Path ".\requirements.txt") {
    Write-Host "Installing required packages..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found. Skipping package installation."
}

# 4️⃣ Git operations
Write-Host "Adding files to Git..."
git add .

Write-Host "Committing changes..."
git commit -m "Update: E-commerce dashboard"

# Remove existing origin if it exists
git remote remove origin 2>$null

# Add your GitHub repository
git remote add origin https://github.com/mmandloi1501/ecommerce_dashboard.git

Write-Host "Pushing to GitHub..."
git branch -M main
git push -u origin main -f

Write-Host "✅ Deployment to GitHub completed!"
