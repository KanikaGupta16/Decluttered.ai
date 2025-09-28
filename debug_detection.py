#!/usr/bin/env python3
"""
Debug Detection and Cropping
Test YOLO detection and coordinate handling directly
"""

import os
from ultralytics import YOLO
from PIL import Image, ImageDraw
import glob

def debug_detection():
    """Debug YOLO detection and cropping"""

    # Find a test image
    test_images = glob.glob("captures/*.jpg")
    if not test_images:
        print("❌ No test images found in captures/ folder")
        return

    test_image = test_images[0]
    print(f"🔍 Testing detection on: {test_image}")

    # Load YOLO model
    model = YOLO('yolov9c.pt')

    # Run detection
    results = model.predict(
        source=test_image,
        conf=0.25,
        save=False,
        verbose=False
    )

    # Load original image
    img = Image.open(test_image)
    img_width, img_height = img.size
    print(f"📏 Image size: {img_width}x{img_height}")

    # Create a copy for drawing bounding boxes
    debug_img = img.copy()
    draw = ImageDraw.Draw(debug_img)

    detections = {}

    print("\n🎯 Detections:")
    for result in results:
        for i, box in enumerate(result.boxes):
            class_id = int(box.cls[0].item())
            class_name = model.names[class_id]
            coords = tuple(int(c) for c in box.xyxy[0].tolist())
            confidence = float(box.conf[0].item())

            x_min, y_min, x_max, y_max = coords
            width = x_max - x_min
            height = y_max - y_min
            area = width * height

            print(f"  {i+1}. {class_name} (conf: {confidence:.2f})")
            print(f"     Coords: {coords}")
            print(f"     Size: {width}x{height} (area: {area})")

            # Store detection
            coords_key = str(coords)
            detections[coords_key] = class_name

            # Draw bounding box
            draw.rectangle([x_min, y_min, x_max, y_max], outline="red", width=3)
            draw.text((x_min, y_min-20), f"{class_name} {confidence:.2f}", fill="red")

    # Save debug image with bounding boxes
    debug_img.save("debug_detections.jpg")
    print(f"\n📷 Saved debug image with bounding boxes: debug_detections.jpg")

    # Test cropping each detection
    print("\n✂️  Testing crops:")
    os.makedirs("debug_crops", exist_ok=True)

    for i, (coords_key, class_name) in enumerate(detections.items()):
        # Parse coordinates
        coords_str = coords_key.strip("()")
        coords = tuple(map(int, coords_str.split(", ")))
        x_min, y_min, x_max, y_max = coords

        # Crop with 30% border
        object_width = x_max - x_min
        object_height = y_max - y_min
        border_x = int(object_width * 0.3)
        border_y = int(object_height * 0.3)

        new_x_min = max(0, x_min - border_x)
        new_y_min = max(0, y_min - border_y)
        new_x_max = min(img_width, x_max + border_x)
        new_y_max = min(img_height, y_max + border_y)

        crop_coords = (new_x_min, new_y_min, new_x_max, new_y_max)
        cropped = img.crop(crop_coords)

        # Save crop
        crop_filename = f"debug_crops/{i+1}_{class_name}.jpg"
        cropped.save(crop_filename)

        print(f"  {i+1}. {class_name}")
        print(f"     Original: {coords}")
        print(f"     Expanded: {crop_coords}")
        print(f"     Saved: {crop_filename}")
        print(f"     Crop size: {cropped.size}")

    print(f"\n✅ Debug complete! Check debug_detections.jpg and debug_crops/ folder")

if __name__ == "__main__":
    debug_detection()