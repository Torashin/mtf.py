import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector, Button
import numpy as np
import mtf as mtf
import os
import glob


class ROISelector:
    def __init__(self):
        self.roi = None
        self.fig, self.ax = plt.subplots()
        self.rect_selector = None
        self.original_xlim = None
        self.original_ylim = None

        # Button for confirming ROI
        self.button_ax = plt.axes([0.7, 0.05, 0.2, 0.075])
        self.button = Button(self.button_ax, 'Confirm ROI', color='lightblue', hovercolor='lightgreen')
        self.button.on_clicked(self.confirm_roi)

        # Button for resetting zoom
        self.zoom_button_ax = plt.axes([0.05, 0.05, 0.2, 0.075])
        self.zoom_button = Button(self.zoom_button_ax, 'Reset Zoom', color='lightblue', hovercolor='lightgreen')
        self.zoom_button.on_clicked(self.reset_zoom)

        self.selecting_roi = False

    def on_select(self, eclick, erelease):
        if self.selecting_roi:
            self.roi = (int(eclick.xdata), int(eclick.ydata), int(erelease.xdata), int(erelease.ydata))

    def confirm_roi(self, event):
        if self.roi is None:
            print("No ROI selected yet.")
        else:
            print(f"ROI selected: {self.roi}")
            plt.close()

    def reset_zoom(self, event):
        if self.original_xlim is not None and self.original_ylim is not None:
            self.ax.set_xlim(self.original_xlim)
            self.ax.set_ylim(self.original_ylim)
            self.ax.set_aspect('equal', adjustable='box')
            self.fig.canvas.draw()

    def select_roi(self, imgArr):
        self.ax.clear()  # Clear previous image if any
        self.ax.imshow(imgArr, cmap='gray', vmin=0.0, vmax=1.0)
        self.ax.set_title('Zoom/Pan the image and click the button to confirm ROI selection.')

        # Store the initial axis limits
        self.original_xlim = self.ax.get_xlim()
        self.original_ylim = self.ax.get_ylim()

        # Initialize RectangleSelector without rectprops
        self.rect_selector = RectangleSelector(self.ax, self.on_select,
                                               useblit=True, interactive=True)
        self.selecting_roi = True

        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
        plt.show()
        self.selecting_roi = False

        if self.roi is None:
            raise ValueError("No ROI selected. Please select a valid area.")
        return self.roi

def get_roi(image_path):
    imgArr = mtf.Helper.LoadImageAsArray(image_path)
    roi_selector = ROISelector()
    roi = roi_selector.select_roi(imgArr)
    return roi

def process_image(image_path, frequency, roi=None):
    """
    Process a single image to calculate the MTF value for a given frequency.

    Parameters:
    - image_path: str, path to the image file
    - frequency: float, frequency at which to calculate the MTF
    - roi: tuple, (x1, y1, x2, y2) coordinates for region of interest (optional)

    Returns:
    - float: MTF value at the given frequency
    """
    # Load the image as a numpy array
    imgArr = mtf.Helper.LoadImageAsArray(image_path)

    # Check for ROI and crop image if necessary
    if roi:
        x1, y1, x2, y2 = roi
        imgArr = imgArr[y1:y2, x1:x2]

    # Check if imgArr is empty or invalid
    if imgArr.size == 0:
        #print(f"Error: Image array is empty after cropping for {image_path}")
        return None

    # Calculate MTF from the image array with no verbosity
    try:
        res = mtf.MTF.CalculateMtf(imgArr, verbose=mtf.Verbosity.NONE)
    except Exception as e:
        #print(f"Error calculating MTF for {image_path}: {e}")
        return None

    # Get MTF value for the given frequency
    try:
        mtf_value = mtf.MTF.GetMtfValue(res, frequency)
    except Exception as e:
        #print(f"Error getting MTF value for {image_path}: {e}")
        return None

    return mtf_value


def batch_process(directory_path, frequency):
    """
    Process all images in a directory to calculate the MTF value for a given frequency for each image.

    Parameters:
    - directory_path: str, path to the directory containing image files
    - frequency: float, frequency at which to calculate the MTF
    """
    # Define patterns to search for .jpg, .jpeg, and .png files up to 4 levels deep
    file_pattern = os.path.join(directory_path, '**', '*.[jp][pn]g')
    jpeg_pattern = os.path.join(directory_path, '**', '*.jpeg')

    # Use glob.glob with recursive=True to enable searching in subfolders
    image_paths = sorted(glob.glob(file_pattern, recursive=True) + glob.glob(jpeg_pattern, recursive=True))

    # Filter the results to limit the search depth to 4 levels
    image_paths = [path for path in image_paths if len(path.split(os.sep)) - len(directory_path.split(os.sep)) <= 4]

    if not image_paths:
        raise ValueError("No images found in the specified directory.")

    # Get ROI from the first image
    first_image_path = image_paths[0]
    roi = get_roi(first_image_path)


    results = {}
    for path in image_paths:
        try:
            mtf_value = process_image(path, frequency, roi)
            if mtf_value is None:
                pass
                #print(f"MTF value for {path} at frequency {frequency} couldn't be calculated.")
            else:
                results[path] = mtf_value
                print(f"MTF value for {path} at frequency {frequency:.3f}: {100 * mtf_value:.1f}%")
        except Exception as e:
            pass
            #print(f"Error processing {path}: {e}")

    return results

if __name__ == "__main__":
    # Define the directory path and the frequency of interest
    directory_path = r'path/to/images'  # Replace with your directory path
    frequency = 0.5  # Example frequency for MTF calculation

    # Process the images in the directory
    batch_results = batch_process(directory_path, frequency)

    # Optionally, you can save or further process the results here
    # For example, save to a file or perform additional analysis
