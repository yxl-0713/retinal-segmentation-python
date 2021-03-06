#!/usr/bin/env python3
"""
ECE 471 Project
Ashton Meuser
"""

from datetime import datetime
import logging
import argparse as ap
from object_classes.line_mask import generate_line_mask_list
from object_classes.image_collection import ImageCollection
import image_utils
import svm
from calculate_features import calculate_features
from log_execution import log_execution

@log_execution
def train_model(images, mask_list, k_size, probability):
    """
    Train model with list of images
    """
    logging.info('Calculating, normalizing feature vectors for %d image(s)', len(images))
    vectors_list = [calculate_features(x.image, x.fov_mask, mask_list, k_size) for x in images]
    truth_list = [x.truth for x in images]
    logging.info('Training model with %d image(s)', len(images))
    svm.train(vectors_list, truth_list, probability) # Train SVM, lengthy process

@log_execution
def classify_image(images, mask_list, k_size, save, display):
    """
    Classify pixels of a single image
    """
    if len(images) > 1:
        raise ValueError('Only one image can be classified at once')
    logging.info('Calculating, normalizing feature vectors for image')
    image = images[0] # First and only member
    vectors = calculate_features(image.image, image.fov_mask, mask_list, k_size)
    logging.info('Classifying image pixels')
    probabilities, prediction = svm.classify(vectors)
    svm.assess(image.truth, prediction)
    svm.plot_roc(image.truth, probabilities)

    if save:
        image_utils.save_image(prediction, 'prediction.png')
        logging.info('Saved classified image')
    if display:
        image_utils.display_image(prediction)
        logging.info('Displaying classified image')

def main():
    """
    Run main logic, decide between model training and image classification
    """
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--images', help='Image number(s) from database', nargs='+',
                        type=int, required=True)
    parser.add_argument('-k', '--kernel', help='Neighborhood size', type=int, default=15)
    parser.add_argument('-r', '--rotation', help='Rotational resolution', type=int, default=15)
    parser.add_argument('-t', '--train', help='Train SVM model', action='store_true')
    parser.add_argument('-p', '--proba', help='Probabilistic SVM model', action='store_true')
    parser.add_argument('--drhagis', help='Use DR HAGIS database', action='store_true')
    parser.add_argument('-s', '--save', help='Save image', action='store_true')
    parser.add_argument('-d', '--display', help='Display segmented image', action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose logging', action='store_true')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO # Logging verbosity
    logging.basicConfig(format='%(message)s', level=log_level)

    logging.info('Execution started %s', datetime.now().isoformat())

    database = 'DRHAGIS' if args.drhagis else 'DRIVE'
    logging.info('Reading %d image(s) from %s database', len(args.images), database)
    image_collections = [ImageCollection(x, database) for x in args.images]
    mask_list = generate_line_mask_list(args.kernel, args.rotation)

    if args.train: # Train model, lenthy process
        train_model(image_collections, mask_list, args.kernel, args.proba)
    else: # Classify image, assess accuracy
        classify_image(image_collections, mask_list, args.kernel, args.save, args.display)

if __name__ == '__main__':
    main()
