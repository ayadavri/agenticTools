# Tag and push get-consumer-documents-runtime to Amazon ECR
param(
    [string]$ImageTag = "get-consumer-documents-runtime:latest",
    [string]$EcrRepo = "get-consumer-documents-runtime",
    [string]$Region = "us-east-1",
    [string]$AccountId = "302010998259"
)

$ErrorActionPreference = "Stop"
$Registry = "$AccountId.dkr.ecr.$Region.amazonaws.com"
$RemoteTag = "$Registry/${EcrRepo}:latest"

Write-Host "Authenticating to ECR ($Registry) ..."
# Avoid Windows Docker credential helper failures ("The stub received bad data").
$dockerConfig = Join-Path $env:TEMP "docker-ecr-$EcrRepo"
New-Item -ItemType Directory -Force -Path $dockerConfig | Out-Null
$password = aws ecr get-login-password --region $Region
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("AWS:$password"))
$config = @{ auths = @{ $Registry = @{ auth = $auth } } } | ConvertTo-Json -Depth 3
Set-Content -Path (Join-Path $dockerConfig "config.json") -Value $config
$env:DOCKER_CONFIG = $dockerConfig

Write-Host "Tagging $ImageTag -> $RemoteTag ..."
docker tag $ImageTag $RemoteTag
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Pushing $RemoteTag ..."
docker push $RemoteTag
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done. Image URI: $RemoteTag"
