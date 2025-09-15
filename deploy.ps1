# One-command Fly.io deployment script for Windows PowerShell
Write-Host "🚀 SoulSeer Deployment Script" -ForegroundColor Cyan

# Check if fly CLI is installed
if (-not (Get-Command fly -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Fly CLI..." -ForegroundColor Yellow
    iwr https://fly.io/install.ps1 -useb | iex
}

# Login to Fly (if not already)
Write-Host "Logging into Fly.io..." -ForegroundColor Green
fly auth login

# Create app if it doesn't exist
$appName = "soulseer-$(Get-Random -Maximum 9999)"
Write-Host "Creating app: $appName" -ForegroundColor Green
fly apps create $appName --org personal

# Set all secrets at once (you'll be prompted for values)
Write-Host "Setting environment variables..." -ForegroundColor Green
Write-Host "You'll be prompted for each value. Press Enter to skip optional ones." -ForegroundColor Yellow

$secrets = @(
    "DATABASE_URL",
    "CLERK_SECRET_KEY", 
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "PUBLIC_CLERK_PUBLISHABLE_KEY",
    "PUBLIC_STRIPE_PUBLIC_KEY"
)

$secretValues = @{}
foreach ($secret in $secrets) {
    $value = Read-Host -Prompt "Enter $secret (or press Enter to skip)"
    if ($value) {
        $secretValues[$secret] = $value
    }
}

# Build secrets command
if ($secretValues.Count -gt 0) {
    $secretsCmd = "fly secrets set"
    foreach ($key in $secretValues.Keys) {
        $secretsCmd += " $key='$($secretValues[$key])'"
    }
    Invoke-Expression $secretsCmd
}

# Deploy!
Write-Host "🎯 Deploying to Fly.io..." -ForegroundColor Cyan
fly deploy --config fly.toml --dockerfile Dockerfile.fly

# Get the app URL
Write-Host "✅ Deployment complete!" -ForegroundColor Green
fly apps open

Write-Host "Your app is live at: https://$appName.fly.dev" -ForegroundColor Cyan