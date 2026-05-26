# Build ARM64 image for Amazon Bedrock AgentCore Runtime
param(
    [string]$ImageTag = "get-consumer-documents-runtime:latest",
    [string]$Platform = "linux/arm64"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Building $ImageTag for $Platform ..."
docker buildx build --platform $Platform -t $ImageTag --load .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Done. Push to ECR, then create/update AgentCore Runtime with this image URI."
