import magic

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


# MODELS

image = ["gif", "png", "jpeg", "jpg", "webp", "avif", "apng"]
video = ["mp4", "webm", "ogv"]
audio = ["mp3", "wav", "oga"]
document = ["pdf", "txt", "csv", "json",]
Media = {"image": image, "video": video, "audio": audio, "document": document}

media_extensions = image+video+document+audio
media_ext_val = FileExtensionValidator(
    media_extensions, "Unsupported File format", code="Invalid format")

profile_val = FileExtensionValidator(
    image, "Unsupported file format. Try a valid image format")


def file_size_val(file):
    size = round(file.size/1_048_576, 2)
    file_name = file.name[0:15]+"...." if len(file.name) > 15 else file.name
    allowed_size = 15
    if size > allowed_size:
        raise ValidationError(
            f"{file_name} is greater than {allowed_size}MB", code="Invalid file size")


def media_size_val(file):
    size = round(file.size/1_048_576, 2)
    file_name = file.name[0:15]+"...." if len(file.name) > 15 else file.name
    allowed_size = 10
    if size > allowed_size:
        raise ValidationError(
            f"{file_name} is greater than {allowed_size}MB", code="Invalid file size")


def file_type_validator(file):
    accept = [f"{media}/{exts}" for media, ext in Media.items()
              for exts in ext if media != "document"]
    accept += ["application/pdf",
               "application/json", "text/plain", "text/csv", "audio/mpeg"]
    extension = file.url.split(".")[-1]
    file_name = file.name[0:15]+"...." if len(file.name) > 15 else file.name
    if extension not in audio:
        file_mime_type = magic.from_buffer(file.read(1024), mime=True)
        if file_mime_type not in accept:
            raise ValidationError(
                f" {file_name} is an unsupported file type '{file_mime_type}'", code="Invalid Format")


def image_type_validator(file):
    accept = [f"image/{ext}" for ext in image]
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    if file_mime_type not in accept:
        raise ValidationError(f"Unsupported file type '{file_mime_type}'")
