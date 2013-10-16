CMAKE_MINIMUM_REQUIRED(VERSION 2.8)

PROJECT(BinaryThinning3D )

SET(CMAKE_BUILD_TYPE RELEASE)




# BinaryThinning3D.cxx - standalone file with example of 
#   using itkBinaryThinningImageFilter3D
# BinaryThinningCxx - library with skelet function 
#   from unsigned char * to unsigned char *
# BinaryThinning.c - warpper from C++ to C used with Matlab library

SET(THINNING_DIR IJ_181_ITKBinaryThinningImageFilter3D/Source)
ENABLE_TESTING()

message(STATUS "module path: ${CMAKE_MODULE_PATH} ${CMAKE_ROOT}")
FILE(MAKE_DIRECTORY ${CMAKE_MODULE_PATH}/bin)
FILE(DOWNLOAD 
    "http://www.insight-journal.org/download/downloadbitstream/8176/IJ_181_ITKbinaryThinningImageFilter3D.zip"
    ${CMAKE_MODULE_PATH}/IJ_181_ITKBinaryThinningImageFilter3D/binaryThinning3D.zip
    SHOW_PROGRESS
    )
#MESSAGE (STATUS "CMAKE_BINARY_DIR" ${CMAKE_BINARY_DIR})

#SET(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR}/bin)

SET(EXECUTABLE_OUTPUT_PATH ${CMAKE_SOURCE_DIR}/bin)
SET(LIBRARY_OUTPUT_PATH ${CMAKE_SOURCE_DIR}/bin)

#MESSAGE (STATUS "CMAKE_BINARY_DIR" ${CMAKE_BINARY_DIR})

# berlicka pro nalezeni itk pod windows
# SET(ITK_DIR "C:/Users/mjirik/Downloads/InsightToolkit-3.20.1/itkbin/") 
#SET(ITK_DIR "C:/Program Files (x86)/ITK/lib/InsightToolkit/") 

#INCLUDE(Dart)
INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR}/${THINNING_DIR})

FIND_PACKAGE(ITK REQUIRED)
INCLUDE(${ITK_USE_FILE})

# Alternative to FIND_PACKAGE and INCLUDE is next few lines
#INCLUDE(${CMAKE_SOURCE_DIR}/${THINNING_DIR}/IJMacros.txt)
#SET(Required_Packages
#  ITK
#)
#
#FOREACH(Package ${Required_Packages})
#  LOADPACKAGE(${Package})
#ENDFOREACH(Package)

SET(Libraries
  ${ITK_LIBRARIES} 
)

#ADD_DEFINITIONS(-fPIC )

SET(CurrentExe "BinaryThinning3D")
ADD_EXECUTABLE(${CurrentExe} src/BinaryThinning3D.cxx ) 
TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries})

ADD_TEST(BinaryThinning3DTest BinaryThinning3D 
    ${CMAKE_SOURCE_DIR}/${THINNING_DIR}/img_in.dcm 
    ${CMAKE_SOURCE_DIR}/${THINNING_DIR}/img_out.dcm
    )

SET(CurrentExe "BinaryThinningCxx")
ADD_LIBRARY(${CurrentExe} STATIC src/BinaryThinningCxx.cxx ) 
#ADD_LIBRARY(${CurrentExe} SHARED BinaryThinningCxx.cxx ) 
TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries})

SET(CurrentExe "BinaryThinning")
ADD_LIBRARY(${CurrentExe} STATIC src/BinaryThinning.c ) 
#ADD_LIBRARY(${CurrentExe} SHARED BinaryThinning.c ) 
TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries} "BinaryThinningCxx")

SET(CurrentExe "BinaryThinningTest")
ADD_EXECUTABLE(${CurrentExe} src/BinaryThinningTest.c) 
TARGET_LINK_LIBRARIES(${CurrentExe} BinaryThinning BinaryThinningCxx)


# Shared libraries
SET(CurrentExe "BinaryThinningCxxShared")
ADD_LIBRARY(${CurrentExe} SHARED src/BinaryThinningCxx.cxx ) 
TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries})

SET(CurrentExe "BinaryThinningShared")
ADD_LIBRARY(${CurrentExe} SHARED src/BinaryThinning.c ) 
TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries} "BinaryThinningCxxShared")
