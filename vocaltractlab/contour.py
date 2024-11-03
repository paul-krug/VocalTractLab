
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np

from . import make_file_path

from typing import List
from typing import Optional
from typing import Dict
from typing import Any



def svg_to_paths(
        svg_path,
        units_to_cm=1/37.8,# 37.795275591,
        ):
    
    # Parse the SVG file
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Get namespace
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    
    # Retrieve the viewBox to adjust coordinates
    viewBox = root.attrib.get('viewBox')
    if viewBox:
        viewBox = list(map(float, viewBox.split()))
        canvas_height = viewBox[3]  # 4th value is the height
        y_min = viewBox[1]  # 2nd value is the minimum y value
    else:
        canvas_height = None
        y_min = 0
    
    # Initialize list to hold matplotlib paths
    paths = []
    
    # Find all polyline elements
    for polyline in root.findall('.//svg:polyline', namespace):
        points_str = polyline.attrib['points']
        try:
            polyline.attrib['stroke-dasharray']
            line_style = 'dashed'
        except KeyError:
            line_style = 'solid'
        
        # Split the points string into a flat list of coordinate values
        points_list = points_str.strip().split()
        
        # Convert the list of strings into a list of float tuples [(x1, y1), (x2, y2), ...]
        points = [
            (float(points_list[i]), float(points_list[i+1]))
            for i in range(0, len(points_list), 2)
            ]
        
        # Adjust y-values by flipping them and aligning with the canvas height
        if canvas_height:
            points = [(x, canvas_height - (y - y_min)) for x, y in points]

        if units_to_cm:
            points = [(x * units_to_cm, y * units_to_cm) for x, y in points]
        
        # Convert the list of tuples into a numpy array of shape (M, 2)
        vertices = np.array(points)
        
        # Create a list of codes for the Path (MOVETO for the first point, LINETO for others)
        codes = [Path.MOVETO] + [Path.LINETO] * (len(points) - 1)
        
        # Create the path object and append to the list
        path = Path(vertices, codes)
        paths.append(dict(patch=path, line_style=line_style))
    
    return paths

def plot_contour(
        paths: List[ Dict[ str, Any ] ],
        out_file: Optional[ str ] = None,
        contour_color: str = 'black',
        background_color: str = 'white',
        ax: Optional[ plt.Axes ] = None,
        show: bool = False,
        ):
    if ax is None:
        fig, ax = plt.subplots()
    
    # Set background color
    ax.set_facecolor(background_color)

    # Plot each path
    for p in paths:
        path = p['patch']
        line_style = p['line_style']
        patch = patches.PathPatch(
            path,
            edgecolor=contour_color,
            lw=1.0,
            fill=False,
            linestyle=line_style,
            )
        ax.add_patch(patch)
    
    # Ensure aspect ratio is equal and scale view
    ax.set_aspect('equal')
    ax.autoscale_view()
    ax.set_xlabel('X [cm]')
    ax.set_ylabel('Y [cm]')

    if out_file:
        make_file_path(out_file)
        plt.savefig(out_file)
    if show:
        plt.show()
        plt.close()
    if ax is None:
        plt.close(fig)
    return ax

def plot_contours(
        path_sets: List[List[Path]],
        #output_folder: str,
        out_files: List[str],
        contour_color: str = 'black',
        background_color: str = 'white',
        output_size: tuple[int, int] = (800, 600),  # Output size in pixels, e.g., (800, 600)
        ):
    # Sanity check
    if len( out_files ) != len( path_sets ):
        raise ValueError(
            f"""
            The number of image file paths: {len(out_files)}
            does not match the number of contour paths: {len(path_sets)}.
            """
            )
    
    # Determine the unified bounding box
    all_vertices = np.concatenate(
        [
            p['patch'].vertices
            for paths in path_sets
            for p in paths
            ]
        )
    x_min, y_min = np.min(all_vertices, axis=0)
    x_max, y_max = np.max(all_vertices, axis=0)
    
    # Define the fixed limits based on the unified bounding box
    x_margin, y_margin = 0.05 * (x_max - x_min), 0.05 * (y_max - y_min)
    x_limits = (x_min - x_margin, x_max + x_margin)
    y_limits = (y_min - y_margin, y_max + y_margin)

    print( f"x_limits: {x_limits}" )
    print( f"y_limits: {y_limits}" )

    # Target aspect ratio based on output size
    #output_width, output_height = output_size
    #target_aspect_ratio = output_width / output_height
    #plot_aspect_ratio = (x_limits[1] - x_limits[0]) / (y_limits[1] - y_limits[0])

    ## Determine figure size in inches based on DPI
    #dpi = 100  # DPI for the figure; can be adjusted if needed
    #fig_width, fig_height = output_width / dpi, output_height / dpi

    # Plot and save each frame
    #for i, paths in enumerate(path_sets):
    for paths, image_file in zip( path_sets, out_files ):
        fig, ax = plt.subplots()#figsize=(fig_width, fig_height), dpi=dpi)
        
        ## Set consistent limits and invert y-axis for SVG orientation
        #ax.set_xlim(x_limits)
        #ax.set_ylim(y_limits)
        #ax.invert_yaxis()
        
        ## Calculate padding if plot aspect does not match output aspect
        #if plot_aspect_ratio > target_aspect_ratio:
        #    # Wider plot aspect; add padding top/bottom
        #    actual_height = (x_limits[1] - x_limits[0]) / target_aspect_ratio
        #    padding = (actual_height - (y_limits[1] - y_limits[0])) / 2
        #    ax.set_ylim(y_limits[0] - padding, y_limits[1] + padding)
        #else:
        #    # Taller plot aspect; add padding left/right
        #    actual_width = (y_limits[1] - y_limits[0]) * target_aspect_ratio
        #    padding = (actual_width - (x_limits[1] - x_limits[0])) / 2
        #    ax.set_xlim(x_limits[0] - padding, x_limits[1] + padding)

        for p in paths:
            path = p['patch']
            line_style = p['line_style']
            patch = patches.PathPatch(
                path,
                edgecolor=contour_color,
                lw=1.0,
                fill=False,
                linestyle=line_style,
                )
            ax.add_patch(patch)

        # Set background color for padding regions
        #fig.patch.set_facecolor(background_color)
        #ax.set_facecolor(background_color)
        
        # Ensure aspect ratio is equal and scale view
        ax.set_xlim(x_limits)
        ax.set_ylim(y_limits)
        ax.set_aspect('equal')
        ax.autoscale_view()
        ax.set_xlabel('X [cm]')
        ax.set_ylabel('Y [cm]')
        
        #plt.savefig(f"{output_folder}/frame_{i:03d}.png", bbox_inches='tight', pad_inches=0)
        make_file_path(image_file)
        #plt.savefig(image_file, bbox_inches='tight', pad_inches=0)
        # make sure the height and width ar both even numbers in terms of pixels
        plt.savefig(
            image_file,
            bbox_inches="tight", 
            pad_inches=0,
            #facecolor=background_color
        )
        plt.close(fig)
    return


