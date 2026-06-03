import numpy as np
import cv2

font = cv2.FONT_HERSHEY_COMPLEX

# Load image
img2 = cv2.imread('test.png', cv2.IMREAD_COLOR)
img = cv2.imread('test.png', cv2.IMREAD_GRAYSCALE)

# Binarize image
_, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
# Find contours
contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    # Approximate and draw contour
    approx = cv2.approxPolyDP(cnt, 0.009 * cv2.arcLength(cnt, True), True)
    cv2.drawContours(img2, [approx], 0, (0, 255, 255), 5)

# Show result
cv2.imshow('Contours with Coordinates', img2)

# Exit on 'q'
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.destroyAllWindows()