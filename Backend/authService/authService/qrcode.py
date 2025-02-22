import pyotp
import qrcode
import base64
from io import BytesIO
from rest_framework.response import Response

def generateQRCode(user):
	totp_secret = pyotp.random_base32()
	user.totp_secret = totp_secret
	user.save()

	qr_data = f"otpauth://totp/authService:{user.email}?secret={totp_secret}&issuer=Transcendence"
	qr = qrcode.make(qr_data)
	buffer = BytesIO()
	qr.save(buffer, format="PNG")
	qr_base64 = base64.b64encode(buffer.getvalue().decode('utf-8'))
	return (qr_base64, totp_secret)