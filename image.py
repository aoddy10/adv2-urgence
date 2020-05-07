import base64


def convertImageToBase64(imageFile):
    open(imageFile, "rb") as img_file:
        base64String = base64.b64encode(img_file.read())
    print(base64String)
    return base64String
