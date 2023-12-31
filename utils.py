import os, cv2, shutil, fitz, img2pdf
import numpy as np
from PIL import Image


def get_max_image_dimensions(folder_path):
    max_width = 0
    max_height = 0

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder {folder_path} does not exist.")

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            file_path = os.path.join(folder_path, filename)
            image = cv2.imread(file_path)

            if image is not None:
                height, width, _ = image.shape
                max_width = max(max_width, width)
                max_height = max(max_height, height)

    return max_width


def stitch_all(folder_path, image_list):
    images = []
    output_width = get_max_image_dimensions(folder_path=folder_path)

    for filename in image_list:
        image = cv2.imread(filename)

        if image is not None:
            current_width = image.shape[1]
            border_width = output_width - current_width
            left_border_width = border_width // 2
            right_border_width = border_width - left_border_width

            canvas = np.ones((image.shape[0], output_width, 3), np.uint8) * 255
            canvas[:, left_border_width:left_border_width + current_width, :] = image

            images.append(canvas)
    try:
        combined_image = np.vstack(images)
        return combined_image
    except Exception as e:
        return False


def get_document(image, name):
    # Load the input image using cv2
    output_dir = "output_images"  # Directory to save split images

    split_height = 1555  # Height at which to split the image

    if image is None:
        print("Error: Image not found.")
        return

    height, width, channels = image.shape

    # Check if the split height is within the image's height bounds
    if split_height <= 0 or split_height >= height:
        print("Error: Invalid split height.")
        return

    # Determine the number of splits
    num_splits = height // split_height

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Split the image and save each part
    imgs = []
    start = 0
    split_count = 0

    while start < height:
        end = min(start + split_height, height)
        split_image = image[start:end, :]
        # Save the split image
        output_path = os.path.join(output_dir, f"split_{split_count}.png")
        cv2.imwrite(output_path, split_image)

        # print(f"Saved: {output_path}")
        imgs.append(output_path)
        split_count += 1
        start = end

    
    output_pdf = os.path.join('output', f'{name}_notes.pdf')  # Specify the output PDF path

    with open(output_pdf, 'wb') as pdf_output:
        pdf_output.write(img2pdf.convert(imgs))


def resize_img(image):
    r = 1080 / image.shape[1]
    dim = (1080 ,int(image.shape[0] * r))
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized


# Define a function to remove consecutive rows of all-white pixel
def remove_consecutive_white_rows(image):
    result = []
    white_row_count = 0
    max_consecutive_white_rows = 5  # Adjust as needed

    for row in image:
        if np.all(row == 255):  # Check if the row is all-white
            white_row_count += 1
        else:
            white_row_count = 0

        if white_row_count <= max_consecutive_white_rows:
            result.append(row)

    return np.array(result)



def clean_loop(image):
    while True:
        new_image = remove_consecutive_white_rows(image)
        if np.array_equal(new_image, image):
            break  # No more consecutive white rows to remove
        image = new_image

    return image

def process_image(page, lower_color, upper_color):
    image_list = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
    image = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)
    image_np = np.array(image)

    # Convert BGR to RGB format (if needed)
    image = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

    color_mask = cv2.inRange(image, lower_color, upper_color)
    kernel = np.ones((3, 3), np.uint8)
    openning = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    kernel = np.ones((8, 8), np.uint8)
    closing = cv2.dilate(openning, kernel, iterations=3)

    preserved_highlights = cv2.bitwise_and(image, image, mask=closing)
    gray = cv2.cvtColor(preserved_highlights, cv2.COLOR_RGB2GRAY)
    _, preserved_text = cv2.threshold(gray, 135, 255, cv2.THRESH_BINARY_INV)
    preserved_text = cv2.bitwise_and(preserved_text, preserved_text, mask=closing)

    final_image = 255 - preserved_text
    cleaned_image = clean_loop(final_image)

    resized_img = resize_img(cleaned_image)
    return resized_img


def sys_clean():
    if os.path.exists('output_images'):
        shutil.rmtree('output_images')
    if os.path.exists('uploads'):
        shutil.rmtree('uploads')
    if os.path.exists('output'):
        shutil.rmtree('output')
    if not os.path.exists('uploads'):
        os.mkdir('uploads')
    if not os.path.exists('output'):
        os.mkdir('output')

def get_pdf_info(input_pdf):
    pdf_document = fitz.open(input_pdf)
    total = pdf_document.page_count
    return total


def get_image_list(output_dir):
    images = os.listdir(output_dir)
    images.sort(key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
    image_paths = [os.path.join(output_dir, image) for image in images]
    if not image_paths:
        print("No valid images were processed.")
        return None, None
    return image_paths

