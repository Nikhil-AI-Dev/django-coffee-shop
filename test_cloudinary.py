import cloudinary
import cloudinary.uploader

cloudinary.config(
  cloud_name = 'dcpvmnlzu',
  api_key = '187258463573331',
  api_secret = 'QmTA0Ci2GemhGpGUTLIyfM5gQC8'
)

result = cloudinary.uploader.upload(r"C:\Users\nikhi\Downloads\delicious-quality-coffee-cup.jpg")
print("Uploaded:", result['secure_url'])
