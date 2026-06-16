import time
import board
from datetime import datetime
import smtplib  # Για την αποστολή email ειδοποίησης
from email.mime.text import MIMEText
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button

# Εισαγωγή βιβλιοθηκών Hardware
import ST7735
from pyhuskylens import HuskyLens

# ==========================================
# 1. ΑΡΧΙΚΟΠΟΙΗΣΗ HARDWARE
# ==========================================
# Φυσικό κουμπί αλληλεπίδρασης στο GPIO 21 (με εσωτερική αντίσταση pull-up)
btn_info = Button(21)

# Αρχικοποίηση HuskyLens μέσω I2C (Bus 1)
try:
    husky = HuskyLens(1)
    print("HuskyLens συνδέθηκε επιτυχώς!")
except Exception as e:
    print(f"Σφάλμα σύνδεσης HuskyLens: {e}")
    husky = None

# Αρχικοποίηση 1.8" LCD Οθόνης (ST7735)
disp = ST7735.ST7735(
    port=0, cs=0, dc=24, rst=25,
    width=128, height=160, rotation=90, invert=False
)
disp.begin()

WIDTH, HEIGHT = disp.width, disp.height
image = Image.new("RGB", (WIDTH, HEIGHT), "BLACK")
draw = ImageDraw.Draw(image)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except IOError:
    font = ImageFont.load_default()
    font_small = ImageFont.load_default()

# ==========================================
# 2. ΡΥΘΜΙΣΕΙΣ ΑΣΘΕΝΟΥΣ & ΕΠΙΚΟΙΝΩΝΙΑΣ
# ==========================================
MEDICATION_INFO = "Metrhsh Zaxarou\n& Xapi: 14:00"

# Στοιχεία για την αποστολή SOS Email (Αντικαταστήστε με τα δικά σας)
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_robot_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Google App Password
PARENTS_EMAIL = "parents_email@gmail.com"
DOCTOR_EMAIL = "doctor_email@gmail.com"

def send_sos_alert():
    """Συναρτήση που στέλνει Email Έκτακτης Ανάγκης"""
    print("[SOS] Energoopoihsh Eidopoihshs... Apostoli Email!")
    msg_content = f"EKT AKTH ANAGKH: O mathitis xrisimopoiise th xeironomia SOS stis {datetime.now().strftime('%H:%M:%S')}. Parakalo epikoinoniste amesa!"
    
    try:
        msg = MIMEText(msg_content)
        msg['Subject'] = "⚠️ SOS: Eidopoihsh apo Robot-Voitho"
        msg['From'] = SENDER_EMAIL
        msg['To'] = f"{PARENTS_EMAIL}, {DOCTOR_EMAIL}"

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [PARENTS_EMAIL, DOCTOR_EMAIL], msg.as_string())
        server.quit()
        print("[SOS] Ta Email stalthkan epityxos!")
    except Exception as e:
        print(f"[SOS Error] Apotyxia apostolis: {e}")

# ==========================================
# 3. ΛΕΙΤΟΥΡΓΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ ΟΘΟΝΗΣ
# ==========================================
def display_screen(title, line1, line2, bg_color=(44, 62, 80), text_color=(255, 255, 255)):
    """Σχεδιάζει και ανανεώνει την οθόνη LCD"""
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=bg_color)
    draw.text((5, 5), title, fill=(26, 188, 156), font=font)
    draw.line([(0, 22), (WIDTH, 22)], fill=(236, 240, 241), width=1)
    
    draw.text((5, 40), line1, fill=text_color, font=font_small)
    draw.text((5, 75), line2, fill=text_color, font=font_small)
    
    disp.display(image)

# ==========================================
# 4. ΚΥΡΙΟΣ ΒΡΟΧΟΣ (MAIN LOOP)
# ==========================================
print("O Robot-Voithos Ygeias ksekinise!")

last_check_time = time.time()
CHECK_INTERVAL = 30  # Ρωτάει πώς νιώθει κάθε 30 δευτερόλεπτα (προσαρμόστε το)
sos_mode = False

try:
    while True:
        current_time = time.time()
        time_str = datetime.now().strftime("%H:%M:%S")

        # ---------------------------------------------------------
        # Α. ΛΕΙΤΟΥΡΓΙΑ SOS (Έλεγχος Κάμερας HuskyLens)
        # ---------------------------------------------------------
        if husky:
            try:
                blocks = husky.get_blocks()
                if blocks:
                    for block in blocks:
                        # Αν το ID 1 είναι η εκπαιδευμένη χειρονομία SOS
                        if block.id == 1:
                            sos_mode = True
                            display_screen("⚠️ EMERGENCY ⚠️", "EKT AKTH ANAGKH!", "Eidopoihsh Goneon..", bg_color=(231, 76, 60))
                            send_sos_alert()
                            time.sleep(10) # Παύση για να μην στέλνει συνεχόμενα email
            except Exception as e:
                print(f"HuskyLens Read Error: {e}")

        # Αν είμαστε σε κατάσταση SOS, παρακάμπτουμε τα υπόλοιπα μηνύματα μέχρι το reset
        if sos_mode:
            if btn_info.is_pressed:  # Το κουμπί λειτουργεί και ως Reset του SOS
                sos_mode = False
                print("[Robot] To SOS akyrothike apo to xristi.")
                time.sleep(1)
            continue

        # ---------------------------------------------------------
        # Β. ΚΟΥΜΠΙ ΑΛΛΗΛΕΠΙΔΡΑΣΗΣ (Εμφάνιση Αγωγής)
        # ---------------------------------------------------------
        if btn_info.is_pressed:
            print("[Button] Emfanish pliroforion agogis.")
            display_screen("PROGRAMMA AGOGHS", MEDICATION_INFO, "Ygeia pano apo ola!", bg_color=(52, 152, 219))
            time.sleep(4)  # Κρατάει τις πληροφορίες στην οθόνη για 4 δευτερόλεπτα
            continue

        # ---------------------------------------------------------
        # Γ. ΤΑΚΤΙΚΟΣ ΕΛΕΓΧΟΣ (Πώς νιώθεις;)
        # ---------------------------------------------------------
        if current_time - last_check_time >= CHECK_INTERVAL:
            print("[Check] Erwthsh gia thn katastash ygeias.")
            display_screen("ELEGXOS YGEIAS", "Pos niotheis?", "Kane th xeironomia SOS\nan den eisai kala.", bg_color=(241, 196, 15), text_color=(0,0,0))
            time.sleep(5)  # Αφήνει το μήνυμα ερώτησης για 5 δευτερόλεπτα
            last_check_time = time.time()
            continue

        # ---------------------------------------------------------
        # Δ. ΚΑΝΟΝΙΚΗ ΛΕΙΤΟΥΡΓΙΑ (Αναμονή / Ρολόι)
        # ---------------------------------------------------------
        display_screen("HEALTH ASSISTANT", f"Ora: {time_str}", "Katastash: OK\nPatiste to koumpi\ngia thn agwgh.")
        time.sleep(1)

except KeyboardInterrupt:
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill="BLACK")
    disp.display(image)
    print("\nTo robot apenergopoihthike.")
