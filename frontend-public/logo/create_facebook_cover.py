from PIL import Image, ImageDraw
import os

# Facebook cover dimensions (recommended for both desktop and mobile)
COVER_WIDTH = 820
COVER_HEIGHT = 462

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
main_logo_path = os.path.join(script_dir, "logo_package_new/logo_package/logo_HD_2000x2000.png")
sec_logo_path = os.path.join(script_dir, "sec-logo.png")
tesda_logo_path = os.path.join(script_dir, "tesda-logo.png")
output_path = os.path.join(script_dir, "facebook_cover.png")

def create_facebook_cover():
    # Create a white background
    cover = Image.new('RGB', (COVER_WIDTH, COVER_HEIGHT), (255, 255, 255))

    # Add a subtle gradient/accent bar at top and bottom using brand blue
    draw = ImageDraw.Draw(cover)
    brand_blue = (30, 80, 150)  # Dark blue matching the logo

    # Top accent bar
    draw.rectangle([0, 0, COVER_WIDTH, 6], fill=brand_blue)
    # Bottom accent bar
    draw.rectangle([0, COVER_HEIGHT - 6, COVER_WIDTH, COVER_HEIGHT], fill=brand_blue)

    # Load and place main logo (Bright Horizons Institute)
    # Position it to the RIGHT of center to avoid profile picture overlap
    main_logo = Image.open(main_logo_path).convert("RGBA")
    main_logo_height = 220
    main_logo_ratio = main_logo.width / main_logo.height
    main_logo_width = int(main_logo_height * main_logo_ratio)
    main_logo = main_logo.resize((main_logo_width, main_logo_height), Image.LANCZOS)

    # Place main logo right of center (avoiding left side where profile pic sits)
    main_x = 280  # Shifted right to avoid profile picture area
    main_y = (COVER_HEIGHT - main_logo_height) // 2
    cover.paste(main_logo, (main_x, main_y), main_logo)

    # Load SEC logo
    sec_logo = Image.open(sec_logo_path).convert("RGBA")
    sec_height = 90
    sec_ratio = sec_logo.width / sec_logo.height
    sec_width = int(sec_height * sec_ratio)
    sec_logo = sec_logo.resize((sec_width, sec_height), Image.LANCZOS)

    # Load TESDA logo
    tesda_logo = Image.open(tesda_logo_path).convert("RGBA")
    tesda_height = 90
    tesda_ratio = tesda_logo.width / tesda_logo.height
    tesda_width = int(tesda_height * tesda_ratio)
    tesda_logo = tesda_logo.resize((tesda_width, tesda_height), Image.LANCZOS)

    # Place TESDA on LEFT, SEC on RIGHT - both vertically centered like main logo
    margin = 120

    # TESDA on the left (adjusted for even spacing)
    tesda_x = 150
    tesda_y = (COVER_HEIGHT - tesda_height) // 2
    cover.paste(tesda_logo, (tesda_x, tesda_y), tesda_logo)

    # SEC on the right (similar spacing as TESDA)
    sec_x = COVER_WIDTH - sec_width - 120
    sec_y = (COVER_HEIGHT - sec_height) // 2
    cover.paste(sec_logo, (sec_x, sec_y), sec_logo)

    # Save the cover
    cover.save(output_path, 'PNG', quality=95)
    print(f"Facebook cover created: {output_path}")
    print(f"Dimensions: {COVER_WIDTH} x {COVER_HEIGHT} pixels")

if __name__ == "__main__":
    create_facebook_cover()
