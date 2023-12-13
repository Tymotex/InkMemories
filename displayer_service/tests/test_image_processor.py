import unittest
from image_processor import determine_central_crop_coordinates, central_crop

class TestImageProcessorDetermineCropCoordinates(unittest.TestCase):
    def test_determine_central_crop_coordinates_wide(self):
        expected_crop_coordinates = (250, 0, 750, 500)
        actual_crop_coordinates = determine_central_crop_coordinates(1000, 500, 1)
        self.assertEqual(expected_crop_coordinates, actual_crop_coordinates)
    
    def test_determine_central_crop_coordinates_square(self):
        expected_crop_coordinates = (0, 0, 1000, 1000)
        actual_crop_coordinates = determine_central_crop_coordinates(1000, 1000, 1)
        self.assertEqual(expected_crop_coordinates, actual_crop_coordinates)

    def test_determine_central_crop_coordinates_tall(self):
        expected_crop_coordinates = (0, 250, 500, 750)
        actual_crop_coordinates = determine_central_crop_coordinates(500, 1000, 1)
        self.assertEqual(expected_crop_coordinates, actual_crop_coordinates)

    def test_determine_central_crop_coordinates_wide_crop(self):
        expected_crop_coordinates = (0, 450, 1000, 550)
        actual_crop_coordinates = determine_central_crop_coordinates(1000, 1000, 10)
        self.assertEqual(expected_crop_coordinates, actual_crop_coordinates)


if __name__ == "__main__":
    unittest.main()
