#ifndef BINARY_THINNING_H
#define BINARY_THINNING_H

#if defined(WIN32)                   // MS Windows
    #define DllImport   __declspec( dllimport )
#else
    #define DllImport
#endif

DllImport int thinningIncrement (int a);
DllImport unsigned char * thinning(int sizeX, int sizeY, int sizeZ, unsigned char * data  );

#endif // BINARY_THINNING_H
