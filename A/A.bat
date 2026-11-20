@echo off
setlocal

set "SCRIPT_DIR=%USERPROFILE%\Documents\Scripts"
set "PS_SCRIPT=%SCRIPT_DIR%\Watch-NewDrives.ps1"
set "TASK_NAME=WatchNewDrives"

if not exist "%SCRIPT_DIR%" mkdir "%SCRIPT_DIR%"

:: Write the PowerShell watcher script saving to %USERPROFILE%\Documents\MountedDriveCopies
> "%PS_SCRIPT%" echo $DestinationRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) "MountedDriveCopies"
>> "%PS_SCRIPT%" echo New-Item -ItemType Directory -Path $DestinationRoot -Force ^| Out-Null
>> "%PS_SCRIPT%" echo $KnownDrives = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
>> "%PS_SCRIPT%" echo Get-PSDrive -PSProvider FileSystem ^| ForEach-Object { if ($_.Name -match '^[D-Z]$') { [void]$KnownDrives.Add("$($_.Name):") } }
>> "%PS_SCRIPT%" echo while ($true) {
>> "%PS_SCRIPT%" echo     $CurrentDrives = Get-PSDrive -PSProvider FileSystem ^| Where-Object { $_.Name -match '^[D-Z]$' }
>> "%PS_SCRIPT%" echo     $CurrentNames = @($CurrentDrives ^| ForEach-Object { "$($_.Name):" })
>> "%PS_SCRIPT%" echo     foreach ($Existing in @($KnownDrives)) { if ($CurrentNames -notcontains $Existing) { [void]$KnownDrives.Remove($Existing) } }
>> "%PS_SCRIPT%" echo     foreach ($Drive in $CurrentDrives) {
>> "%PS_SCRIPT%" echo         $RootPath = "$($Drive.Name):\"
>> "%PS_SCRIPT%" echo         if (-not $KnownDrives.Contains($Drive.Name + ":") -and (Test-Path $RootPath)) {
>> "%PS_SCRIPT%" echo             [void]$KnownDrives.Add($Drive.Name + ":")
>> "%PS_SCRIPT%" echo             $Stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
>> "%PS_SCRIPT%" echo             $Label = if ($Drive.Description) { ($Drive.Description -replace '[^\w\-]', '_') } else { "Drive_$($Drive.Name)" }
>> "%PS_SCRIPT%" echo             $TargetDir = Join-Path $DestinationRoot "${Stamp}_${Label}_$($Drive.Name)"
>> "%PS_SCRIPT%" echo             robocopy $RootPath $TargetDir /E /R:1 /W:1 /NFL /NDL /NJH /NJS ^| Out-Null
>> "%PS_SCRIPT%" echo         }
>> "%PS_SCRIPT%" echo     }
>> "%PS_SCRIPT%" echo     Start-Sleep -Seconds 2
>> "%PS_SCRIPT%" echo }

:: Replace any existing task and register the hidden logon task under the current user
schtasks /Create /TN "%TASK_NAME%" /SC ONLOGON /TR "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File \"%PS_SCRIPT%\"" /F >nul
if errorlevel 1 (
    echo Failed to create scheduled task "%TASK_NAME%".
    pause
    exit /b 1
)

:: Start the updated task right now in the background
schtasks /Run /TN "%TASK_NAME%" >nul
if errorlevel 1 (
    echo Task created, but failed to start immediately. It will run on next logon.
    pause
    exit /b 1
)

echo Done. Saving to Documents\MountedDriveCopies and "%TASK_NAME%" is running in the background.
pause
