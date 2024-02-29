import requests
import qrcode
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.pyplot as plt
import io
import shutil
import matplotlib.image as mpimg


from PIL import Image, ImageDraw
TOKEN_USER = open("config.txt").readline()
VERSION = 5.199
file_path=''

response = requests.get('https://api.vk.com/method/users.get',
params={'access_token': TOKEN_USER,
        'fields': 'education, activities, about, bdate, connections,photo_400_orig,contacts,city,interests,status,career',
        'v': VERSION
        })
data = response.json()['response'][0]
def color_to_hex(color_name):
    colors = {
        "бордовый": "#800020",
        "чёрный": "#000000",
        "бирюзовый": "#40e0d0",
        "салатовый": "#7fff00",
        "синий": "#0000ff",
        "фиолетовый": "#800080"
    }

    return colors.get(color_name.lower(), "Цвет не найден")

def read_color_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        color_name = file.read().strip()
        return color_to_hex(color_name)
file_path = 'color.txt'
color_user = read_color_from_file(file_path)

def set_style():
    # Set font
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'STIXGeneral'
def save_image_from_url(image_url, file_path):
        try:
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                        with open(file_path, 'wb') as out_file:
                                shutil.copyfileobj(response.raw, out_file)
                        del response
                        print("Фотография успешно сохранена как", file_path)
                else:
                        print("Не удалось загрузить фотографию")
        except Exception as e:
                print("Произошла ошибка при сохранении фотографии:", e)


image_url = data['photo_400_orig']
save_image_from_url(image_url, file_path)


def create_qr_code(url, scale=6):
        # Generate QR code
        qr = qrcode.QRCode(
                version=3,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,  # Increase box_size instead of scaling later
                border=0,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white').get_image().convert("RGB")

        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        byte_arr.seek(0)  # Seek back to the beginning of the BytesIO object
        return byte_arr


def add_qr_code(fig, ax, url):
        qr_code = create_qr_code(url)
        imagebox = OffsetImage(plt.imread(qr_code), zoom=0.2)
        ab = AnnotationBbox(imagebox, (0.86, 0.09))
        ax.add_artist(ab)


def wrap_text(text, max_count):
        words = text.split()
        wrapped_text = ''
        count = 0
        for word in words:
                if count + len(word) > max_count:
                        wrapped_text += '\n' + word
                        count = len(word)
                else:
                        if count != 0:
                                wrapped_text += ' ' + word
                                count += len(word) + 1
                        else:
                                wrapped_text += word
                                count += len(word)
        return wrapped_text


def count_lines(text):
        return text.count('\n') + 1


def display_profile(data, color_user):
        set_style()
        fig, ax = plt.subplots(figsize=(11.69, 8.27))

        plt.annotate("Резюме сформированo из данных пользователя на странице Вконтакте", (.02, .98),
                     weight='regular', fontsize=8, alpha=.6)
        plt.annotate(data['first_name'] + " " + data['last_name'], (.02, .94), weight='bold', fontsize=20)
        plt.annotate(data['city']['title'], (.02, .91), weight='regular', fontsize=14)
        plt.annotate(data['mobile_phone'], (.7, .75), weight='regular', fontsize=10)

        plt.annotate("Обо мне", (0.02, .86), weight='bold', fontsize=10, color=color_user)
        plt.annotate(wrap_text(data['about'], 60), (.02, .86 - 0.07 * count_lines(data['about'])), weight='regular',
                     fontsize=10)

        start_y_position = .745  # Initial y position for the first career entry
        vertical_shift = 0.15  # Adjust this value to create space between career entries
        plt.annotate("Карьера", (.02, .745), weight='bold', fontsize=10, color=color_user)
        for i, career_entry in enumerate(data['career']):
                y_position = start_y_position - i * vertical_shift
                plt.annotate(str(i + 1) + ". " + career_entry['company'], (.02, y_position - 0.04), weight='bold',
                             fontsize=10)
                plt.annotate(str(career_entry['from']) + "-" + str(career_entry['until']), (.02, y_position - 0.08),
                             weight='regular', fontsize=9, alpha=0.6)
                plt.annotate(career_entry['position'], (.02, y_position - 0.12), weight='regular', fontsize=9)

        plt.annotate("Образование", (.02, .3), weight='bold', fontsize=10, color=color_user)
        plt.annotate(data['university_name'], (.02, .3 - 0.04), weight='bold', fontsize=10)
        plt.annotate(data['faculty_name'], (.02, .3 - 0.04 * 2), weight='regular', fontsize=9, alpha=.6)
        plt.annotate("Год окончания: " + str(data['graduation']), (.02, .3 - 0.04 * 3), weight='regular', fontsize=9)
        plt.annotate(data['education_status'], (.02, .3 - 0.04 * 4), weight='regular', fontsize=10)

        plt.annotate("Интересы", (.7, .7), weight='bold', fontsize=10, color=color_user)
        plt.annotate(wrap_text(data['interests'], 39), (.7, .65 - 0.07 * count_lines(data['interests'])),
                     weight='regular', fontsize=10)
        plt.annotate("Деятельность", (.7, .5), weight='bold', fontsize=10, color=color_user)
        plt.annotate(wrap_text(data['activities'], 39), (.7, .47 - 0.07 * count_lines(data['activities'])),
                     weight='regular', fontsize=10)
        plt.axis('off')  # Turn off the axis

        filename_prefix = "Резюме " + data['first_name'] + " " + data['last_name']
        add_qr_code(fig, ax, 'https://vk.com/id' + str(data['id']))  # Replace with the actual URL

        # Load and process the image
        img = mpimg.imread('название_файла.jpg')
        imagebox = OffsetImage(img, zoom=0.2)
        ab = AnnotationBbox(imagebox, (0.85, 0.89), frameon=False, pad=0.2)
        ax.add_artist(ab)

        DECORATIVE_LINE_COLOR = '#007ACC'
        DECORATIVE_LINE_ALPHA = 0.0
        DECORATIVE_LINE_WIDTH = 100
        # Add decorative lines
        ax.axvline(x=.5, ymin=0, ymax=1, color=DECORATIVE_LINE_COLOR, alpha=DECORATIVE_LINE_ALPHA,
                   linewidth=DECORATIVE_LINE_WIDTH)
        plt.axvline(x=.99, color='#000000', alpha=0.5, linewidth=400)

        # Save as PDF
        plt.savefig(f"{filename_prefix}.pdf", format="pdf")  # Save as PDF

        # Save as PNG
        plt.savefig(f"{filename_prefix}.png", format="png")  # Save as PNG
        plt.show()


display_profile(data, color_user)
