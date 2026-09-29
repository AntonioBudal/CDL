Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)

pythonExe = currentDir & "\backend\.venv\Scripts\python.exe"
scriptPy = currentDir & "\iniciar.py"

' Executa 100% invisivel em segundo plano (0 = oculto, False = nao bloqueia execucao)
cmd = """" & pythonExe & """ """ & scriptPy & """ --host 0.0.0.0 --port 8000"
WshShell.CurrentDirectory = currentDir
WshShell.Run cmd, 0, False
