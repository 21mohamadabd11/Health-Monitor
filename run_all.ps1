# Percorso della venv (batch activate per cmd)
$venvPath = "C:\Users\franc\OneDrive - Politecnico di Torino\progetto\venv\Scripts\activate.bat"

$scripts = @(
    "C:\Users\franc\OneDrive - Politecnico di Torino\progetto\catalog\catalog.py",
    "C:\Users\franc\OneDrive - Politecnico di Torino\progetto\healthConnector\devConnector\devCon.py",
    "C:\Users\franc\OneDrive - Politecnico di Torino\progetto\houseConnector\devConnector\devCon.py",
    "C:\Users\franc\OneDrive - Politecnico di Torino\progetto\StatisticProvider\StatisticProvider.py",
    "C:\Users\franc\OneDrive - Politecnico di Torino\progetto\TelegramBot\DoctorBot.py",
    "C:\Users\franc\OneDrive - Politecnico di Torino\progetto\TelegramBot\PatientBot.py",
    "C:\Users\franc\OneDrive - Politecnico di Torino\progetto\ThingSpeakAdaptor\datiTest.py"
)

foreach ($scriptPath in $scripts) {
    $scriptDir  = Split-Path $scriptPath
    $scriptName = Split-Path $scriptPath -Leaf

    # Costruisco la stringa di comandi da eseguire dentro cmd
    $cmdCommands = "color 07 && cd /d `"$scriptDir`" && call `"$venvPath`" && python `"$scriptName`""

    # Start-Process per aprire cmd.exe con i comandi specificati
    Start-Process "cmd.exe" -ArgumentList "/k $cmdCommands"
}
