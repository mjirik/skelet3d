CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
INCLUDE(${CMAKE_SOURCE_DIR}/IJMacros.txt)

PROJECT(BinaryThinning3D )

SET(CMAKE_BUILD_TYPE RELEASE)




# BinaryThinning3D.cxx - standalone file with example of 
#   using itkBinaryThinningImageFilter3D
# BinaryThinningCxx - library with skelet function 
#   from unsigned char * to unsigned char *
# BinaryThinning.c - warpper from C++ to C used with Matlab library

ENABLE_TESTING()

message(STATUS "module path: ${CMAKE_MODULE_PATH} ${CMAKE_ROOT}")

# berlicka pro nalezeni itk pod windows
# SET(ITK_DIR "C:/Users/mjirik/Downloads/InsightToolkit-3.20.1/itkbin/") 
SET(ITK_DIR "C:/Program Files (x86)/ITK/lib/InsightToolkit/") 

INCLUDE(Dart)

SET(Required_Packages
  ITK
)
#
FOREACH(Package ${Required_Packages})
  LOADPACKAGE(${Package})
ENDFOREACH(Package)

SET(Libraries
  ${ITK_LIBRARIES} 
#  ITKBasicFilters
#  ITKCommon
#  ITKIO
)

ADD_DEFINITIONS(-fPIC )

#IF(BUILD_TESTING)
  SET(CurrentExe "BinaryThinning3D")
  ADD_EXECUTABLE(${CurrentExe} BinaryThinning3D.cxx) 
  TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries})
#ENDIF(BUILD_TESTING)

ADD_TEST(BinaryThinning3DTest BinaryThinning3D ${CMAKE_SOURCE_DIR}/img_in.dcm ${CMAKE_SOURCE_DIR}/img_out.dcm)

SET(CurrentExe "BinaryThinningCxx")
ADD_LIBRARY(${CurrentExe} STATIC BinaryThinningCxx.cxx ) 
#ADD_LIBRARY(${CurrentExe} SHARED BinaryThinningCxx.cxx ) 
TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries})

  SET(CurrentExe "BinaryThinning")
  ADD_LIBRARY(${CurrentExe} STATIC BinaryThinning.c ) 
  #ADD_LIBRARY(${CurrentExe} SHARED BinaryThinning.c ) 
  TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries} "BinaryThinningCxx")

  SET(CurrentExe "BinaryThinningTest")
  ADD_EXECUTABLE(${CurrentExe} BinaryThinningTest.c) 
  TARGET_LINK_LIBRARIES(${CurrentExe} BinaryThinning BinaryThinningCxx)


