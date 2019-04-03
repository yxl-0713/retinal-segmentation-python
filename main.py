#!/usr/bin/env python3
"""
ECE 471 Project
Ashton Meuser
"""

from time import time
import argparse as ap
import numpy as np
from convolve import convolve
import image_utils
from model.line_mask import generate_line_mask_list
from line_score import line_score
from create_fov_mask import create_fov_mask
from classify import train, classify, assess

def main():
    """
    Run the program
    Avoids globals
    """
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--image', help='Image number from database', type=int, required=True)
    parser.add_argument('-k', '--kernel', help='Window size', type=int, default=15)
    parser.add_argument('-r', '--resolution', help='Rotation resolution', type=int, default=15)
    parser.add_argument('-s', '--save', help='Save image', action='store_true')
    parser.add_argument('-d', '--display', help='Display image', action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
    args = parser.parse_args()

    start = time()

    image = image_utils.read_image('DRIVE/image/{:02d}_test.tif'.format(args.image))
    image = image_utils.get_inverse_green_channel(image)
    fov_mask = create_fov_mask('DRIVE/mask/{:02d}_test_mask.tif'.format(args.image), args.kernel)
    mask_list = generate_line_mask_list(args.kernel, args.resolution)
    function = lambda x, y: line_score(x, y, mask_list)
    result = convolve(image, args.kernel, function, fov_mask, 2, verbose=args.verbose)
    # line_score_image = result[:, :, 0].astype(np.uint8)

    truth = image_utils.read_image('DRIVE/truth/{:02d}_test_truth.tif'.format(args.image),
                                   greyscale=True).astype(np.bool)
    model = train(result, truth)
    prediction = classify(result, model)
    # image_utils.display_image(prediction)
    assess(truth, prediction)

    stop = time()

    if args.verbose:
        print('time elapsed: {:.2f}s'.format(stop - start))

    # if args.save:
    #     image_utils.save_image(line_score_image, 'output.png')
    # if args.display:
    #     image_utils.display_image(cv2.bitwise_not(line_score_image))

if __name__ == '__main__':
    main()
