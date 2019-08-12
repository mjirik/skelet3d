CMAKE_MINIMUM_REQUIRED(VERSION 2.8)

PROJECT(BinaryThinning3D )

SET(CMAKE_BUILD_TYPE RELEASE)

# version controlled with bumpversion
SET(PACKAGE_VERSION 1.7.13)



# BinaryThinning3D.cxx - standalone file with example of
#   using itkBinaryThinningImageFilter3D
# BinaryThinningCxx - library with skelet function
#   from unsigned char * to unsigned char *
# BinaryThinning.c - warpper from C++ to C used with Matlab library

SET(THINNING_DIR IJ_181_ITKBinaryThinningImageFilter3D)
ENABLE_TESTING()

message(STATUS "module path: ${CMAKE_MODULE_PATH} ${CMAKE_ROOT}")
FILE(MAKE_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)
#message(STATUS "Downloading binary thinning code")
FIND_PATH(THINNING_DOWNLOADED NAME BinaryThinning3D.cxx PATHS ${CMAKE_SOURCE_DIR}/${THINNING_DIR}/Source)
message("thinning_downloaded ${THINNING_DOWNLOADED}")
IF (NOT THINNING_DOWNLOADED)
FILE(DOWNLOAD
    # "http://www.insight-journal.org/download/downloadbitstream/8176/IJ_181_ITKbinaryThinningImageFilter3D.zip"
    # "http://147.228.240.61/queetech/install/IJ_181_ITKbinaryThinningImageFilter3D.zip"
    "http://home.zcu.cz/~mjirik/lisa/install/IJ_181_ITKbinaryThinningImageFilter3D.zip"
    ${CMAKE_SOURCE_DIR}/${THINNING_DIR}/binaryThinning3D.zip
    #${CMAKE_BINARY_DIR}/binaryThinning3D.zip
    SHOW_PROGRESS
    )

ENDIF(NOT THINNING_DOWNLOADED)


message(STATUS "Unzipping")

IF(WIN32)
    #^SET(ITK_DIR "C:/Program Files (x86)/ITK/lib/InsightToolkit/")
    FIND_PROGRAM(UNZIP "unzip" PATH "C:/Program Files (x86)/GnuWin32/bin")
ELSE()
    SET(UNZIP "unzip")
ENDIF()

MESSAGE("UNZIP application: ${UNZIP}")


ADD_CUSTOM_TARGET(unzipped_source
    COMMAND ${UNZIP} -o ${CMAKE_SOURCE_DIR}/${THINNING_DIR}/binaryThinning3D.zip -d ${CMAKE_SOURCE_DIR}/${THINNING_DIR}
    #DEPENDS ${CMAKE_SOURCE_DIR}/${THINNING_DIR}/
    #DEPENDS ${CMAKE_BINARY_DIR}/BinaryThinning3D.zip
    )


#MESSAGE (STATUS "CMAKE_BINARY_DIR" ${CMAKE_BINARY_DIR})

#SET(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR}/bin)

SET(EXECUTABLE_OUTPUT_PATH ${CMAKE_SOURCE_DIR}/bin)
SET(LIBRARY_OUTPUT_PATH ${CMAKE_SOURCE_DIR}/bin)

#MESSAGE (STATUS "CMAKE_BINARY_DIR" ${CMAKE_BINARY_DIR})
MESSAGE(STATUS "CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}")
# message(STATUS "CMAKE_ROOT: ${CMAKE_ROOT} ${CMAKE_PREFIX_PATH}")


# berlicka pro nalezeni itk pod windows a linuxem
FIND_PATH(ITK_DIR NAME "ITKConfig.cmake" PATHS
    $ENV{HOME}/Downloads/InsightToolkit-3.20.1/itkbin/
    "C:/Program Files (x86)/ITK/lib/InsightToolkit/"
    "/usr/lib/InsightToolkit"
    #    $ENV{HOME}/anaconda/
    #    $ENV{HOME}/anaconda2/
    )
#IF (WIN32)
# SET(ITK_DIR "C:/Users/mjirik/Downloads/InsightToolkit-3.20.1/itkbin/")
# SET(ITK_DIR "C:/Program Files (x86)/ITK/lib/InsightToolkit/")
#ENDIF (WIN32)

# pro nalezeni na linuxu lze specifikovat pomoci
# IF (UNIX)
#  SET(ITK_DIR "/usr/lib/InsightToolkit/")
# CMAKE_MODULE_PATH("/usr/lib/InsightToolkit/ITKConfig.cmake")
# ENDIF (UNIX)

MESSAGE(STATUS "ITK_DIR after little help ${ITK_DIR}")

#INCLUDE(Dart)
INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR}/${THINNING_DIR}/Source)

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


ADD_TEST(BinaryThinning3DTest BinaryThinning3D
    ${CMAKE_SOURCE_DIR}/${THINNING_DIR}/Source/img_in.dcm
    ${CMAKE_SOURCE_DIR}/${THINNING_DIR}/Source/img_out.dcm
    )


# Static libraries
IF(BUILD_STATIC)
    SET(CurrentExe "BinaryThinningCxx")
    ADD_LIBRARY(${CurrentExe} STATIC src/BinaryThinningCxx.cxx )
    TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries})

    ADD_DEPENDENCIES(BinaryThinningCxx unzipped_source )

    SET(CurrentExe "BinaryThinning")
    ADD_LIBRARY(${CurrentExe} STATIC src/BinaryThinning.c )
    TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries} "BinaryThinningCxx")
ENDIF()


# Executable
SET(CurrentExe "BinaryThinningTest")
ADD_EXECUTABLE(${CurrentExe} src/BinaryThinningTest.c)
#TARGET_LINK_LIBRARIES(${CurrentExe} BinaryThinning BinaryThinningCxx)
TARGET_LINK_LIBRARIES(${CurrentExe} BinaryThinningShared BinaryThinningCxxShared)
ADD_DEPENDENCIES(${CurrentExe} unzipped_source )

SET(CurrentExe "BinaryThinning3D")
ADD_EXECUTABLE(${CurrentExe} src/BinaryThinning3D.cxx )
TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries})
ADD_DEPENDENCIES(${CurrentExe} unzipped_source )

# Shared libraries
SET(CurrentExe "BinaryThinningCxxShared")
ADD_LIBRARY(${CurrentExe} SHARED src/BinaryThinningCxx.cxx )
TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries})
ADD_DEPENDENCIES(${CurrentExe} unzipped_source )

SET(CurrentExe "BinaryThinningShared")
ADD_LIBRARY(${CurrentExe} SHARED src/BinaryThinning.c )
TARGET_LINK_LIBRARIES(${CurrentExe} ${Libraries} "BinaryThinningCxxShared")

ADD_DEPENDENCIES(BinaryThinningShared unzipped_source )


# where should be installed so libraries
FIND_PATH(CONDA_PREFIX NAME "LICENSE.txt" PATHS
    $ENV{HOME}/miniconda/
    $ENV{HOME}/miniconda2/
    $ENV{HOME}/anaconda/
    $ENV{HOME}/anaconda2/
    )
# alternative you can use conda info --root

# MESSAGE("cmake install prefix " ${CMAKE_INSTALL_PREFIX} )
# MESSAGE("conda prefix " ${CONDA_PREFIX} )
# MESSAGE("home dir" $ENV{HOME} )

# this is not working ctypes cannot find lib in conda directory
# problem is that we need build python with normal user and install with sudo
# IF(CONDA_PREFIX)
#     # MESSAGE("conda nalezena")
#     SET(SKELET3D_LIB_INSTALL_DESTINATION ${CONDA_PREFIX}/lib/python2.7/site-packages)
#
# ELSE()
#     # MESSAGE("conda nenalezena")
#     SET(SKELET3D_LIB_INSTALL_DESTINATION lib)
# ENDIF()

SET(SKELET3D_LIB_INSTALL_DESTINATION lib)
MESSAGE("install prefix " ${CMAKE_INSTALL_PREFIX})
MESSAGE("skelet3d lib install dir " ${SKELET3D_LIB_INSTALL_DESTINATION})
INSTALL(TARGETS BinaryThinningCxxShared DESTINATION ${SKELET3D_LIB_INSTALL_DESTINATION})

# IF(NOT NO_SHARED_INSTALL)
    # SET(SKELET3D_LIB_INSTALL_DESTINATION "./")
    # INSTALL(TARGETS BinaryThinningCxxShared )
# ENDIF()

## --------------------------- Python compilation -----------------------
# it is not necessary to build python package this way
# it can be installed independently on shared libraries

FIND_PROGRAM(PYTHON "python")

IF (PYTHON)
    MESSAGE(status "python executable ${PYTHON}")
    # SET(SETUP_PY_IN "${CMAKE_CURRENT_SOURCE_DIR}/src/setup.py.in")
    SET(SETUP_PY_IN "${CMAKE_CURRENT_SOURCE_DIR}/setup.py")
    SET(SETUP_PY    "${CMAKE_CURRENT_BINARY_DIR}/setup.py")
    #set(DEPS        "${CMAKE_CURRENT_SOURCE_DIR}/module/__init__.py")
    SET(OUTPUT      "${CMAKE_CURRENT_BINARY_DIR}/timestamp")

    CONFIGURE_FILE(${SETUP_PY_IN} ${SETUP_PY})

    # "setup.py build" create build/build dir otherwise there is fail in touch command
    ADD_CUSTOM_COMMAND(OUTPUT ${OUTPUT}
                        COMMAND ${PYTHON} ${SETUP_PY} build
                        COMMAND ${CMAKE_COMMAND} -E touch ${OUTPUT}
                        #DEPENDS ${DEPS}
                        )

    ADD_CUSTOM_TARGET(target ALL DEPENDS ${OUTPUT})

    IF(NO_SETUPPY)
        MESSAGE(DEPRECATION "Use INSTALL_PYTHON_PACKAGE instead of deprecated NO_SETUPPY variable with inverse logic")
    ENDIF(NO_SETUPPY)
    IF(INSTALL_PYTHON_PACKAGE)
        MESSAGE(STATUS "install skelet3d into python")
        FIND_PROGRAM(PIP "pip")
        IF (PIP)
            # INSTALL(CODE "execute_process(COMMAND ${PIP} install ${CMAKE_BINARY_DIR})")
            INSTALL(CODE "execute_process(COMMAND ${PIP} install .)")
        ELSE()
            INSTALL(CODE "execute_process(COMMAND ${PYTHON} ${SETUP_PY} install)")
        ENDIF()
    ENDIF(INSTALL_PYTHON_PACKAGE)
ENDIF()






