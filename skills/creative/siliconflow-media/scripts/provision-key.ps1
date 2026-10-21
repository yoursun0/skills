$ErrorActionPreference = 'Stop'
$credentialDir = Join-Path $env:LOCALAPPDATA 'SiliconFlowMedia'
$credentialFile = Join-Path $credentialDir 'api-key.dpapi'
if (Test-Path -LiteralPath $credentialFile) {
    throw 'A credential already exists. Remove that exact file locally if you intend to replace it.'
}
$secret = Read-Host 'SiliconFlow API key (local masked entry; never paste into chat)' -AsSecureString
try {
    if ($secret.Length -eq 0) { throw 'An empty credential cannot be provisioned.' }
    New-Item -ItemType Directory -Path $credentialDir -Force | Out-Null
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    & icacls.exe $credentialDir /inheritance:r /grant:r "${identity}:(OI)(CI)F" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Could not restrict the credential directory ACL.' }
    $encrypted = $secret | ConvertFrom-SecureString
    [IO.File]::WriteAllText($credentialFile, $encrypted, [Text.Encoding]::ASCII)
    Write-Output 'Credential provisioned with Windows DPAPI. No network request was made.'
} finally {
    if ($secret) { $secret.Dispose() }
    Remove-Variable secret, encrypted -ErrorAction SilentlyContinue
}
