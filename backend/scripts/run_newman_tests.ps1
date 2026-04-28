param(
    [string]$CollectionPath = (Join-Path $PSScriptRoot '..\aub_reviews.postman_collection.json'),
    [string]$EnvironmentPath = (Join-Path $PSScriptRoot '..\aub_reviews.postman_environment.json'),
    [string]$DotEnvPath = (Join-Path $PSScriptRoot '..\.env')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-DotEnvValue {
    param(
        [string]$Path,
        [string]$Name
    )

    if (-not (Test-Path $Path)) {
        return $null
    }

    foreach ($line in Get-Content $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith('#')) {
            continue
        }

        $parts = $trimmed.Split('=', 2)
        if ($parts.Count -ne 2) {
            continue
        }

        $key = $parts[0].Trim()
        if ($key -ne $Name) {
            continue
        }

        $value = $parts[1].Trim()
        if ($value.StartsWith('"') -and $value.EndsWith('"')) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        elseif ($value.StartsWith("'") -and $value.EndsWith("'")) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        return $value
    }

    return $null
}

function Resolve-ApiBaseUrl {
    $candidates = @(
        $env:API_BASE_URL,
        $env:BACKEND_URL,
        (Get-DotEnvValue -Path $DotEnvPath -Name 'API_BASE_URL'),
        (Get-DotEnvValue -Path $DotEnvPath -Name 'BACKEND_URL'),
        'http://localhost:8000'
    )

    $candidate = $candidates | Where-Object { $_ -and $_.Trim() } | Select-Object -First 1
    if (-not $candidate) {
        $candidate = 'http://localhost:8000'
    }

    $candidate = $candidate.TrimEnd('/')
    if ($candidate -match '/api/v1$') {
        return [pscustomobject]@{
            BaseUrl = $candidate
            RootUrl = $candidate.Substring(0, $candidate.Length - 7).TrimEnd('/')
        }
    }

    return [pscustomobject]@{
        BaseUrl = "$candidate/api/v1"
        RootUrl = $candidate
    }
}

$apiUrls = Resolve-ApiBaseUrl

Write-Host "Resolved API base URL: $($apiUrls.BaseUrl)"
Write-Host "Resolved API root URL: $($apiUrls.RootUrl)"

$newman = Get-Command newman -ErrorAction SilentlyContinue
if ($newman) {
    & $newman.Source run $CollectionPath `
        -e $EnvironmentPath `
        --env-var "baseUrl=$($apiUrls.BaseUrl)" `
        --env-var "rootUrl=$($apiUrls.RootUrl)" `
        @args
    exit $LASTEXITCODE
}

$npx = Get-Command npx -ErrorAction SilentlyContinue
if (-not $npx) {
    throw 'Neither newman nor npx was found. Install Node.js and Newman, or add newman to PATH.'
}

& $npx.Source --yes newman run $CollectionPath `
    -e $EnvironmentPath `
    --env-var "baseUrl=$($apiUrls.BaseUrl)" `
    --env-var "rootUrl=$($apiUrls.RootUrl)" `
    @args

exit $LASTEXITCODE
