"%PYTHON%" setup.py install
if errorlevel 1 exit 1

:: Add more build steps here, if they are necessary.

:: See
:: http://docs.continuum.io/conda/build.html
:: for a list of environment variables that are set during the build process.



rem Need to handle Python 3.x case at some point (Visual Studio 2010)
if %ARCH%==32 (
  if %PY_VER% LSS 3 (
    set CMAKE_GENERATOR="Visual Studio 14 2015"
    set CMAKE_CONFIG="Release|Win32"
::	set OPENCV_ARCH=x86
::	set OPENCV_VC=vc9
  )
)
if %ARCH%==64 (
  if %PY_VER% LSS 3 (
    set CMAKE_GENERATOR="Visual Studio 14 2015 Win64"
    set CMAKE_CONFIG="Release|x64"
::	set OPENCV_ARCH=x64
::	set OPENCV_VC=vc9
  )
)

mkdir build2
cd build2

cmake .. -G%CMAKE_GENERATOR%

cmake --build . --config %CMAKE_CONFIG% --target ALL_BUILD
cmake --build . --config %CMAKE_CONFIG% --target INSTALL

rem Let's just move the files around to a more sane structure (flat)
move "%LIBRARY_PREFIX%\%OPENCV_ARCH%\%OPENCV_VC%\bin\*.dll" "%LIBRARY_LIB%"
:: move "%LIBRARY_PREFIX%\%OPENCV_ARCH%\%OPENCV_VC%\bin\*.exe" "%LIBRARY_BIN%"
:: move "%LIBRARY_PREFIX%\%OPENCV_ARCH%\%OPENCV_VC%\lib\*.lib" "%LIBRARY_LIB%"
:: rmdir "%LIBRARY_PREFIX%\%OPENCV_ARCH%" /S /Q

rem By default cv.py is installed directly in site-packages
rem Therefore, we have to copy all of the dlls directly into it!
xcopy "%LIBRARY_LIB%\opencv*.dll" "%SP_DIR%"

rem We have to copy libpng.dll and zlib.dll for runtime
rem dependencies, similar to copying opencv above.
:: xcopy "%LIBRARY_BIN%\libpng15.dll" "%SP_DIR%"
:: xcopy "%LIBRARY_BIN%\zlib.dll" "%SP_DIR%"
