from PIL import Image, ImageDraw, ImageFont
import random



overlays = [
    'assets/cat.png', 
    'assets/cat2.png', 
    'assets/cat3.png', 
    'assets/cat4.png', 
    'assets/catfood.png', 
    'assets/eatup.png', 
    'assets/foodbowl.png', 
    'assets/hungry.png', 
    'assets/hungry2.png', 
    'assets/letseat.png', 
    'assets/tasty.png', 
    'assets/yummy.png', 
]


def apply_overlay(background_image, front_file, at_top, at_left):
    frontImage = Image.open(front_file)
    # Convert image to RGBA
    frontImage = frontImage.convert('RGBA')

    width, height = frontImage.size
    target_width = 600
    target_height = int(target_width * (height/width))
    frontImage = frontImage.resize((target_width, target_height))

    if at_left:
        offset_width = 0
    else:
        offset_width = background_image.width - frontImage.width

    if at_top:
        offset_height = 0
    else:
        offset_height = background_image.height - frontImage.height

    background_image.paste(frontImage, (offset_width, offset_height), frontImage)
    return background_image

def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, im1.height))
    return dst

def create_image(side_image, top_image, final_image, imgtext):
    thisImage = Image.open(side_image)

    # Convert image to RGBA
    thisImage = thisImage.convert('RGBA')
    thisImage = get_concat_h(thisImage, Image.open(top_image))

    thisImage = apply_overlay(thisImage, random.choice(overlays), True, False)
    # thisImage = apply_overlay(thisImage, random.choice(overlays), False, True)
    thisImage = apply_overlay(thisImage, 'assets/fixedbanner.png', False, True)

    d = ImageDraw.Draw(thisImage)
    d.multiline_text((100,800), imgtext, font=ImageFont.truetype("/mnt/e/Windows/Fonts/tahoma.ttf", 90), fill=(255,255,255,255))

    # Save this image
    thisImage.save(final_image, format='jpeg')


if __name__ == '__main__':
    create_image('photos/20210620_082150_a.jpg', 'photos/20210620_082150_b.jpg',  'testnew.jpg', 'Just ate 18g of food\nover 90 seconds')