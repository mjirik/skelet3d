% Funkce vypocita skeleton. 
%   skel = itkSkeleton(data)
% data: binarni data v uint8
% 
% Pro spusteni je potreba prelozit binarni cast pomoci cmake. Je nutne mit
% ITK. Pak se pomoci compile.m vytvori mex soubor, ktery je volan v teto
% funkci.
% Starsi varianta pocitala s loadLibrary, kod je castecne zachovan
function skel = skelet3d(data)
skel = binaryThinningMex(uint8(data));

% 
% loadlibrary('libBinaryThinning.so','BinaryThinning.h', 'alias', 'thn')
% % calllib('thn','thinningIncrement',4)
% % libfunctions('thn')
% % libfunctionsview('thn')
% %calllib('thn','thinning',1,1,1,1)
% 
% %t = calllib('thn','thinning',1,1,1,[4 2 3])
% %data = [4 2 3; 1 0 1];
% % data = zeros(20,20,20);
% % data(7:13,8:13,4:16) = 1;
% pdata = libpointer('uint8Ptr',data);
% 
% t = calllib('thn','thinning',size(data,1),size(data,2),size(data,3),pdata);
% 
% out = get(pdata,'Value');
% skel = reshape(out,size(data));
% unloadlibrary('thn')
