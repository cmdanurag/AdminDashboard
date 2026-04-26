from PIL import Image, ImageDraw, ImageFont
import io

def generate_certificate(name: str, event_title: str, date: str) -> bytes:
    img = Image.new('RGB', (1000, 700), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 60)
        font_text = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
        
    d.text((500, 200), "Certificate of Participation", fill=(0, 0, 0), font=font_title, anchor="mm")
    d.text((500, 350), f"This is to certify that", fill=(0, 0, 0), font=font_text, anchor="mm")
    d.text((500, 420), name, fill=(0, 102, 204), font=font_title, anchor="mm")
    d.text((500, 500), f"has successfully participated in {event_title}", fill=(0, 0, 0), font=font_text, anchor="mm")
    d.text((500, 600), f"Date: {date}", fill=(0, 0, 0), font=font_text, anchor="mm")
    
    d.rectangle([20, 20, 980, 680], outline=(0, 0, 0), width=5)
    
    pdf_bytes = io.BytesIO()
    img.save(pdf_bytes, format='PDF', resolution=100.0)
    return pdf_bytes.getvalue()
