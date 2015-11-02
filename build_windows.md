# Build ITK and skelet3d DLL library on Windows 10 64-bit

* Install [cmake](https://cmake.org/), use stable version 3.4.2 ( there are problems with 3.4.0-rc2 when generating 64-bit projects)
* Download [Visual Studio Express](https://www.visualstudio.com/products/visual-studio-community-vs#) with C++ support (select in installation process)
* Download and install [InsightToolkit](http://www.itk.org/) - [video GUI tutorial](https://www.youtube.com/watch?v=f79joU6FTFQ) or with command line:

        mkdir itk-build-64
        cd itk-build-64
        cmake cmake -G "Visual Studio 14 2015 Win64" -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=ON ..\InsightToolkit-4.7.1
        cmake --build . --config Release
        
* Add Insight-toolkit build dir to Windows PATH
* Build skelet3d library

        mkdir build
        cd build
        cmake -G "Visual Studio 14 2015 Win64" -D ITK_DIR=C:/Users/mjirik/Downloads/itk-build-64 ..
        cmake --build . --config Release
        
* Add builded DLL libraries into environment PATH
