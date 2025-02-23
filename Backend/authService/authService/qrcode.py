import qrcode
import base64
from io import BytesIO

def generateQRCode(email, totp_secret):
	qr_data = f"otpauth://totp/authService:{email}?secret={totp_secret}&issuer=Transcendence"
	qr = qrcode.make(qr_data)
	buffer = BytesIO()
	qr.save(buffer, format="PNG")
	qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
	return (qr_base64)