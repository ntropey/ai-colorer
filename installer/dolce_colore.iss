; Inno Setup Script for Dolce Colore
; Published by Revisited Labs (https://revisitedlabs.com)

#define MyAppName "Dolce Colore"
; build_desktop.py passes the real number from app_version.py (/DMyAppVersion=...).
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#define MyAppPublisher "Revisited Labs"
#define MyAppURL "https://revisitedlabs.com"
#define MyAppExeName "DolceColore.exe"

[Setup]
AppId={{8B3F2E14-41A3-4B81-9E52-25D619A86E77}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=..\dist-installer
OutputBaseFilename=DolceColore_Setup_v{#MyAppVersion}
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\DolceColore\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Video colorization needs FFmpeg. We don't bundle it; check for it before installing.
// Photos work without it, so a missing FFmpeg is a warning, never a blocker.
const
  FFmpegDownloadPage = 'https://ffmpeg.org/download.html';

function FFmpegInstalled(): Boolean;
begin
  Result := FileSearch('ffmpeg.exe', GetEnv('PATH')) <> '';
end;

function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;
  if FFmpegInstalled() then
    Exit;

  // A silent install (e.g. an automatic update) answers "No": install and carry on.
  case SuppressibleMsgBox(
    'FFmpeg was not found on this computer.' + #13#10 + #13#10 +
    'Dolce Colore needs FFmpeg to colorize VIDEO. Photo colorization works without it.' + #13#10 + #13#10 +
    'Yes  - Get FFmpeg first (opens the download page and closes Setup)' + #13#10 +
    'No   - Install Dolce Colore now and add FFmpeg later' + #13#10 +
    'Cancel - Quit Setup' + #13#10 + #13#10 +
    'Tip: in Windows Terminal, "winget install Gyan.FFmpeg" installs it in one step. ' +
    'Restart Dolce Colore afterwards so it can find it.',
    mbConfirmation, MB_YESNOCANCEL, IDNO) of
    IDYES:
      begin
        ShellExec('open', FFmpegDownloadPage, '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
        Result := False;
      end;
    IDCANCEL:
      Result := False;
  end;
end;
