@echo off
REM remove-camera-folder-and-filename.bat
REM https://github.com/techknight/llm-scripts
REM
REM This batch file looks in the current directory for directories that contain
REM the string "-Camera" in their names. Inside of those directories, it then removes
REM "-Camera" from any filenames. Finally, the directories also have that string
REM removed from their names.
REM
REM This is useful when rendering a lot product animations using Adobe Substance 3D Stager.
REM
REM Prerequisites:
REM None
REM 
REM Tool:
REM ChatGPT (GPT-4)
REM 
REM Prompt:
REM Write a batch file to do the following:
REM 1. Iterate through all of the directories in the current folder that contain the string "-Camera"
REM 2. In each of those directories, check for files that contain the string "-Camera". For example, "UD-003-Wall-Skulls-2-Camera_18.png".
REM 3. Remove the string "-Camera" from those filenames.
REM 4. After all of the files have been renamed, rename the directories to remove the string "-Camera" from them as well.

setlocal enabledelayedexpansion

REM Iterate through all directories containing "-Camera" in their names
for /D %%d in (*-Camera*) do (
    pushd "%%d"
    
    REM Rename files in the directory containing "-Camera" in their names
    for %%f in (*-Camera*) do (
        set "newName=%%f"
        set "newName=!newName:-Camera=!"
        ren "%%f" "!newName!"
    )
    
    popd
)

REM Rename the directories after all files have been processed
for /D %%d in (*-Camera*) do (
    set "dirName=%%d"
    set "dirName=!dirName:-Camera=!"
    ren "%%d" "!dirName!"
)

endlocal
exit /b
