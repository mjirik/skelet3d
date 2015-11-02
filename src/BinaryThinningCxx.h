#ifndef BINARY_THINNING_3D_H
#define BINARY_THINNING_3D_H

#if defined(WIN32)                   // MS Windows
    #define DllImport   __declspec( dllimport )
#else
    #define DllImport
#endif

#ifdef __cplusplus
extern "C"
#endif
DllImport int thinningCxxIncrement (int a);

#ifdef __cplusplus
extern "C"
#endif
DllImport unsigned char * thinningCxx(int sizeX, int sizeY, int sizeZ, unsigned char * data );

#endif



