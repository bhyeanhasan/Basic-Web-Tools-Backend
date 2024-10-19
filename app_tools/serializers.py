from PIL import Image,UnidentifiedImageError
from rest_framework import serializers
import mimetypes


class TextSummarySerializer(serializers.Serializer):
    text = serializers.CharField(max_length=5000, allow_blank=False, trim_whitespace=False)
    min_length = serializers.IntegerField()
    max_length = serializers.IntegerField()


class SpeedTestResultSerializer(serializers.Serializer):
    download_speed = serializers.FloatField()
    upload_speed = serializers.FloatField()
    ping = serializers.FloatField()


class MarkdownFileSerializer(serializers.Serializer):
    markdown_file = serializers.FileField()

    def validate_markdown_file(self, value):
        if not value.name.endswith('.md'):
            raise serializers.ValidationError("Only Markdown (.md) files are allowed.")
        return value


class PDFFileSerializer(serializers.Serializer):
    pdf_file = serializers.FileField()

    def validate_pdf_file(self, value):
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        return value


class ImageFileSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False
    )

    def validate_images(self, value):
        valid_mime_types = {
            "image/png", "image/jpeg", "image/jpg",
            "image/gif", "image/bmp", "image/tiff"
        }

        for file in value:
            # Detect the MIME type of the uploaded file
            mime_type, _ = mimetypes.guess_type(file.name)

            if mime_type not in valid_mime_types:
                raise serializers.ValidationError(
                    f"Unsupported image format: {mime_type} for file {file.name}."
                )

        return value


class YouTubeDownloadSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)

    def validate_url(self, value):
        if not value.startswith("https://www.youtube.com") and not value.startswith("https://youtube"):
            raise serializers.ValidationError("Invalid YouTube URL.")
        return value
