from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from transformers import pipeline
from .serializers import TextSummarySerializer,SpeedTestResultSerializer
import speedtest

class home(APIView):
    def get(self, request):
        data = {'message': 'Hello, world!'}
        return Response(data)


class SpeedTest(APIView):

    def get(self, request):
        try:
            st = speedtest.Speedtest()

            st.get_best_server()

            download_speed = st.download() / 10 ** 6

            upload_speed = st.upload() / 10 ** 6

            ping_result = st.results.ping

            data = {
                "download_speed": round(download_speed, 2),
                "upload_speed": round(upload_speed, 2),
                "ping": round(ping_result, 2),
            }

            serializer = SpeedTestResultSerializer(data=data)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TextSummarizer(APIView):
    def post(self, request):
        serializer = TextSummarySerializer(data=request.data)

        if serializer.is_valid():
            text = serializer.validated_data['text']
            min_length = serializer.validated_data.get('min_length', 30)
            max_lenght = serializer.validated_data.get('max_length', 130)
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            summary = summarizer(text, max_length=max_lenght, min_length=min_length, do_sample=False)
            return Response({'summary': summary[0]['summary_text']}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
