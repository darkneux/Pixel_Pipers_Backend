import cv2


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (4, 2, 0))


def draw_bounding_boxes_number(image_path, txtfile_path, output_image_path, color, font_scale):
    # Read the image
    image = cv2.imread(image_path)

    # Define the font settings for the text
    font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
    font_scale = font_scale
    font_thickness = 1
    font_color = hex_to_rgb(color)
    shadow_color = (0, 0, 0)  # Black shadow color
    shadow_offset = 1  # Offset for the shadow

    # Read the bounding box data from the text file
    with open(txtfile_path, 'r') as file:
        lines = file.readlines()

    # Sort the bounding box data based on y-coordinate
    lines.sort(key=lambda line: float(line.strip().split()[2]))

    # Process each line in the sorted file
    for i, line in enumerate(lines):
        data = line.strip().split(' ')

        # Extract the bounding box coordinates
        x_center, y_center, width, height = map(float, data[1:])

        # Convert coordinates to integers
        image_width, image_height = image.shape[1], image.shape[0]
        center_x = int(x_center * image_width)
        center_y = int(y_center * image_height)

        # Get the size of the text
        text_size = cv2.getTextSize(str(i + 1), font, font_scale, font_thickness)[0]

        # Calculate the position for the text to be centered within the bounding box
        text_x = int(center_x - text_size[0] / 2)
        text_y = int(center_y + text_size[1] / 2)

        # Draw shadow of the number
        cv2.putText(image, str(i + 1), (text_x + shadow_offset, text_y + shadow_offset), font, font_scale, shadow_color, font_thickness)

        # Draw the number
        cv2.putText(image, str(i + 1), (text_x, text_y), font, font_scale, font_color, font_thickness)

    # Save the image with numbers
    cv2.imwrite(output_image_path, image)
    print(f"Image with numbers saved as {output_image_path}")




def draw_bounding_boxes(image_path, txtfile_path, output_image_path, color):
    # Read the image
    image = cv2.imread(image_path)

    # Define the colors for the dots (BGR format)
    color = hex_to_rgb(color)

    # Read the bounding box data from the text file
    with open(txtfile_path, 'r') as file:
        lines = file.readlines()

    # Process each line in the file
    for line in lines:
        data = line.strip().split(' ')

        # Extract the bounding box coordinates
        x_center, y_center, width, height = map(float, data[1:])

        # Convert coordinates to integers
        image_width, image_height = image.shape[1], image.shape[0]
        center_x = int(x_center * image_width)
        center_y = int(y_center * image_height)

        # Plot a dot at the center of the bounding box
        cv2.circle(image, (center_x, center_y), 4, color, -1)

    # Save the image with dots
    cv2.imwrite(output_image_path, image)
    print(f"Image with dots saved as {output_image_path}")