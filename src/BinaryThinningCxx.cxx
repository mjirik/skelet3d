


#include "itkImage.h"
#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"

#include "itkConnectedThresholdImageFilter.h"
#include "itkImageRegionIterator.h"
#include "itkBinaryThinningImageFilter3D.h"

#include <iostream>
#include <stdlib.h>   // for atoi()


#include "BinaryThinningCxx.h"

using namespace std;

  const   unsigned int Dimension = 3;
  typedef signed short PixelType;   // must be signed for CT since Hounsfield units can be < 0
  typedef itk::Image< PixelType, Dimension > ImageType;

int thinningCxxIncrement (int a){
printf("inkrementCXX");
  return a+2;
}

ImageType::Pointer thinningITK( ImageType::Pointer in){
 // return in;
 // Define the thinning filter
  typedef itk::BinaryThinningImageFilter3D< ImageType, ImageType > ThinningFilterType;
  ThinningFilterType::Pointer thinningFilter = ThinningFilterType::New();
  thinningFilter->SetInput(in);
  thinningFilter->Update();
  return thinningFilter->GetOutput();

}
//char * thinningCxx(int sizeX, int sizeY, int sizeZ, char* data ){
unsigned char * thinningCxx(int sizeX, int sizeY, int sizeZ, unsigned char * data ){
// uncomment next line for debug
//printf("thinnCXX()"); 

//  int ii;
 // for (ii = 0; ii < (sizeX*sizeY*sizeZ) ; ii++){
 //   data[ii] = data[ii] + 2;
 // }
  //return data;

  // vytvoreni vstupnich dat
  ImageType::IndexType start;
	ImageType::SizeType  size;

  size[0]  = sizeX;  // size along X
	size[1]  = sizeY;  // size along Y
	size[2]  = sizeZ;  // size along Z

	start[0] =   0;  // first index on X
	start[1] =   0;  // first index on Y
	start[2] =   0;  // first index on Z


  ImageType::Pointer image = ImageType::New();


	ImageType::RegionType region;
	region.SetSize( size );
	region.SetIndex( start );

	// Pixel data is allocated
	image->SetRegions( region );
	image->Allocate();
  // uncomment next line for debug
  //printf("thinnCxx() printf  \n");
  
  //std::cout << "thinningCxx()\n";  

  // plneni daty
  // pixel init
	ImageType::IndexType pixelIndex;
  int i,j,k;
  for( i = 0; i < sizeX; i++) {
    for( j = 0; j < sizeY; j++) {
      for( k = 0; k < sizeZ; k++) {

        pixelIndex[0] = i;   // x position
        pixelIndex[1] = j;   // y position
				pixelIndex[2] = k;   // z position

        PixelType pixelValue = data[k*sizeX*sizeY + j*sizeX + i] ;

        if (pixelValue > 0){
          // pixelValue = 33769;
          pixelValue = 1001;
        }
        else{
          //pixelValue = 32768;
          pixelValue = 0;
        }

        image->SetPixel(   pixelIndex,  pixelValue  );
      }
    }
  }


  // ztenceni
  //
 // image = thinningITK(image);
typedef itk::BinaryThinningImageFilter3D< ImageType, ImageType > ThinningFilterType;
  ThinningFilterType::Pointer thinningFilter = ThinningFilterType::New();
  thinningFilter->SetInput(image);
  thinningFilter->Update();
  //return thinningFilter->GetOutput();


  // zapis zpet
  for( i = 0; i < sizeX; i++) {
    for( j = 0; j < sizeY; j++) {
      for( k = 0; k < sizeZ; k++) {

        pixelIndex[0] = i;   // x position
        pixelIndex[1] = j;   // y position
				pixelIndex[2] = k;   // z position

        data[k*sizeX*sizeY + j*sizeX + i] = thinningFilter->GetOutput()->GetPixel(   pixelIndex );
       // data[k*sizeX*sizeY + j*sizeX + i] = (unsigned char) k;
//        image->GetPixel(   pixelIndex,  pixelValue  );
      }
    }
  }

  // zapis zpet

  return data;
}



