import mtf as mtf

# Load the image as a numpy array
imgArr = mtf.Helper.LoadImageAsArray(r'slant.png')

# Calculate MTF from the image array with detailed verbosity
res = mtf.MTF.CalculateMtf(imgArr, verbose=mtf.Verbosity.DETAIL)

# Print MTF value for a given frequency
frequency = 0.1
mtf_value = mtf.MTF.GetMtfValue(res, frequency)
print(f"MTF value at frequency {frequency}: {100*mtf_value:.1f}%")