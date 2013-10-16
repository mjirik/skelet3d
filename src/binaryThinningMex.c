#include "mex.h"
#include "BinaryThinningCxx.h"

/*
 * timestwo.c - example found in API guide
 *
 * Computational function that takes a scalar and doubles it.
 *
 * This is a MEX-file for MATLAB.
 * Copyright 1984-2011 The MathWorks, Inc.
 */
 
/* $Revision: 1.8.6.5 $ */




/*unsigned char * */
void thinningMx(unsigned char *y[], unsigned char data[], const mwSize *dims)
{
  /*y[0] = 2.0*x[0];*/
  int sizeX, sizeY, sizeZ;
  sizeX = (int) dims[0];
  sizeY = (int) dims[1];
  sizeZ = (int) dims[2];
  /* *y[1] = 20;  */
  /* *y = thinningCxx(sizeX, sizeY, sizeZ, data); */
  /*y = thinningCxx(10, 10, 10, data);*/
  mexWarnMsgTxt("Jsme v thinningMx()");
/*   y = thinningCxx(10, 10, 10, data);*/
  printf("Hoja hoj printf, inkrement %i \n", thinningCxxIncrement (2));
  
   /* *y[1] = 19;  */
   /* return y;*/
}

void mexFunction( int nlhs, mxArray *plhs[],
                  int nrhs, const mxArray *prhs[] )
{
  int sizeX, sizeY, sizeZ;
  
  unsigned char *x, *y, *ytmp;
  unsigned char **px, **py;
  int i; 
  size_t mrows,ncols;
  /*mwSize number_of_dims;
  mwSize dims[] = mxGetDimensions(prhs[0]);*/
  const mwSize *dims;

  
  
  /* Check for proper number of arguments. */
  if(nrhs!=1) {
    mexErrMsgIdAndTxt( "MATLAB:timestwo:invalidNumInputs",
            "One input required.");
  } else if(nlhs>1) {
    mexErrMsgIdAndTxt( "MATLAB:timestwo:maxlhs",
            "Too many output arguments.");
  }
  
  /* The input must be a noncomplex uint8.*/
  mrows = mxGetM(prhs[0]);
  ncols = mxGetN(prhs[0]);
  if( !mxIsUint8(prhs[0]) || mxIsComplex(prhs[0])
      ) {
    mexErrMsgIdAndTxt( "MATLAB:timestwo:inputNotRealScalarDouble",
            "Input must be a noncomplex uint8.");
  }
  
  /*number_of_dims = mxGetNumberOfDimensions(prhs[0]);*/
  
   
  /* Create matrix for the return argument. */
  dims = mxGetDimensions(prhs[0]);
          /* create a 2-by-2 array of unsigned 16-bit integers */
    plhs[0] = mxCreateNumericArray(mxGetNumberOfDimensions(prhs[0]), mxGetDimensions(prhs[0]),mxUINT8_CLASS,mxREAL);
  /*plhs[0] = mxCreateDoubleMatrix((mwSize)mrows, (mwSize)ncols, mxREAL);*/
  
  /* Assign pointers to each input and output. */
  x = (unsigned char *) mxGetData(prhs[0]);
  y = (unsigned char *) mxGetData(plhs[0]);
  /*py = (unsigned char **) mxGetPr(plhs[0]); */
  
  py = &y;
  /* Call the thinning subroutine. */
  printf ("x[0] = %i\n", x[0]);
  y[3] = 3;
  
  sizeX = (int) dims[0];
  sizeY = (int) dims[1];
  sizeZ = (int) dims[2];
  
  /* thinningMx(py,x, dims); */
  ytmp = thinningCxx(sizeX, sizeY, sizeZ, x);
  
  for (i = 0; i < sizeX*sizeY*sizeY; i++){
      y[i] = ytmp[i];
  }
  /**py[3] = 2; */
  /*py[2] = 1;*/
  
}
