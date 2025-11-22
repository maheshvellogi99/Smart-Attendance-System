import qrcode

# Create a QR code instance
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Add data
qr.add_data('Prem Sai')
qr.make(fit=True)

# Create an image from the QR Code
qr_image = qr.make_image(fill_color="black", back_color="white")

# Save the image
qr_image.save('test_barcode.png')
print("Test barcode generated as 'test_barcode.png'") 