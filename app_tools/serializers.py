from rest_framework import serializers


class TextSummarySerializer(serializers.Serializer):
    text = serializers.CharField(max_length=5000, allow_blank=False, trim_whitespace=False)
    min_length = serializers.IntegerField()
    max_length = serializers.IntegerField()


class SpeedTestResultSerializer(serializers.Serializer):
    download_speed = serializers.FloatField()
    upload_speed = serializers.FloatField()
    ping = serializers.FloatField()
