% Compilation
% maybe you will need run: 
% mex -setup


% mex libBinaryThinningCxx.a libBinaryThinning.a binaryThinningMex.c
% mex libBinaryThinningCxx.a binaryThinningMex.c


% Compiles mex files
% clc; clear all; cd mex;

if ispc
    % not tested
    disp('PC');
    itkDir = '"C:/Program Files (x86)/ITK"'
    itkIncludeDir = '"C:/Program Files (x86)/ITK/include"'
    itkLibDir = '"C:/Program Files (x86)/ITK/lib/InsightToolkit/"'
    include = [' -I' itkIncludeDir ];
    libpath = itkLibDir;
    
    files = dir([libpath '*.lib']);
    
    lib = [];
    for i = 1:length(files),
        lib = [lib ' ' libpath files(i).name];
    end
    
    eval(['mex bin/libBinaryThinningCxx.a binaryThinningMex.c -O' include lib]);
%     include = ' -Ic:\OpenCV-2.3_trunk_20120324_build_64_install\include\opencv\ -Ic:\OpenCV-2.3_trunk_20120324_build_64_install\include\';
%     libpath = 'c:\OpenCV-2.3_trunk_20120324_build_64_install\lib\';
%     files = dir([libpath '*.lib']);
    
%     lib = [];
%     for i = 1:length(files),
%         lib = [lib ' ' libpath files(i).name];
%     end
%     
%     eval(['mex lk.cpp -O' include lib]);
%     mex -O -c tld.cpp
%     mex -O fern.cpp tld.obj
%     mex -O linkagemex.cpp
%     mex -O bb_overlap.cpp
%     mex -O warp.cpp
%     mex -O distance.cpp
end

if ismac
    %not tested
    disp('Mac');
    
    include = ' -I/opt/local/include/opencv/ -I/opt/local/include/'; 
    libpath = '/opt/local/lib/'; 
    
    files = dir([libpath 'libopencv*.dylib']);
    
    lib = [];
    for i = 1:length(files),
        lib = [lib ' ' libpath files(i).name];
    end
    
    eval(['mex lk.cpp -O' include lib]);
    mex -O -c tld.cpp
    mex -O fern.cpp tld.o
    mex -O linkagemex.cpp
    mex -O bb_overlap.cpp
    mex -O warp.cpp
    mex -O distance.cpp
    
end

if isunix
    disp('Unix');
    
    include = ' -I/usr/local/include/InsightToolkit/ -I/usr/local/include/';
    libpath = '/usr/local/lib/InsightToolkit/';
    
    files = dir([libpath 'lib*.so.3.20.1']);
    
    lib = [];
    for i = 1:length(files),
        lib = [lib ' ' libpath files(i).name];
    end
    
    eval(['mex bin/libBinaryThinningCxx.a binaryThinningMex.c -O' include lib]);
%     mex -O -c tld.cpp
%     mex -O fern.cpp tld.o
%     mex -O linkagemex.cpp
%     mex -O bb_overlap.cpp
%     mex -O warp.cpp
%     mex -O distance.cpp
    
end



disp('Compilation finished.');

