import shutil
import time
import zipfile
import pdfkit
import img2pdf
import markdown
import speedtest
from pdf2docx import Converter
from transformers import pipeline
from .serializers import TextSummarySerializer, SpeedTestResultSerializer, MarkdownFileSerializer, PDFFileSerializer, ImageFileSerializer,YouTubeDownloadSerializer
from pdf2image import convert_from_path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import tempfile
from django.http import FileResponse, HttpResponse, StreamingHttpResponse
import yt_dlp


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


class MarkdownToPDFView(APIView):

    def post(self, request):
        serializer = MarkdownFileSerializer(data=request.data)

        if serializer.is_valid():
            try:
                md_file = serializer.validated_data['markdown_file']
                md_content = md_file.read().decode('utf-8')
                html_content = markdown.markdown(md_content)
                pdf_file_path = "output.pdf"
                pdfkit.from_string(html_content, pdf_file_path)
                response = FileResponse(open(pdf_file_path, 'rb'), as_attachment=True, filename='output.pdf')
                return response

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PDFToDOCXView(APIView):
    def post(self, request):
        serializer = PDFFileSerializer(data=request.data)

        if serializer.is_valid():
            try:
                pdf_file = serializer.validated_data['pdf_file']

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    for chunk in pdf_file.chunks():
                        temp_pdf.write(chunk)
                    temp_pdf_path = temp_pdf.name

                docx_file_path = 'output.docx'
                cv = Converter(temp_pdf_path)
                cv.convert(docx_file_path, start=0, end=None)
                cv.close()
                response = FileResponse(open(docx_file_path, 'rb'), as_attachment=True, filename='output.docx')
                os.remove(temp_pdf_path)
                return response

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PDFToIMGView(APIView):
    def post(self, request):
        serializer = PDFFileSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    for chunk in serializer.validated_data['pdf_file'].chunks():
                        temp_pdf.write(chunk)
                    temp_pdf_path = temp_pdf.name

                images = convert_from_path(temp_pdf_path, dpi=250)

                zip_file_path = tempfile.mktemp(suffix=".zip")

                with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, img in enumerate(images):
                        image_path = f'page-{i}.png'
                        img.save(image_path, 'PNG')
                        zip_file.write(image_path, f'page-{i}.png')
                        os.remove(image_path)

                os.remove(temp_pdf_path)

                zip_file_handle = open(zip_file_path, 'rb')

                response = FileResponse(
                    zip_file_handle, as_attachment=True, filename='images.zip'
                )
                response['Content-Disposition'] = 'attachment; filename="images.zip"'
                response['Content-Length'] = os.path.getsize(zip_file_path)
                return response

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImagesToPDFView(APIView):
    def post(self, request):
        serializer = ImageFileSerializer(data=request.data)
        if serializer.is_valid():
            try:
                image_paths = []
                for img_file in serializer.validated_data['images']:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
                        img_file.seek(0)
                        temp_img.write(img_file.read())
                        image_paths.append(temp_img.name)
                image_paths.reverse()
                pdf_file_path = 'output.pdf'
                with open(pdf_file_path, "wb") as pdf_file:
                    layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297)))
                    pdf_file.write(img2pdf.convert(image_paths, layout=layout))
                for path in image_paths:
                    os.remove(path)
                pdf_file = open(pdf_file_path, 'rb')
                response = FileResponse(pdf_file, as_attachment=True, filename='output.pdf')
                return response
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class YouTubeDownloadView(APIView):
    def post(self, request):
        serializer = YouTubeDownloadSerializer(data=request.data)

        if serializer.is_valid():
            url = serializer.validated_data['url']

            try:
                temp_dir = tempfile.mkdtemp()

                ydl_opts = {
                    'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
                    'format': 'bestvideo+bestaudio/best',
                    'noprogress': True,
                    'quiet': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                time.sleep(1)

                video_file = next(
                    (os.path.join(temp_dir, f) for f in os.listdir(temp_dir)
                     if f.endswith(('.mp4', '.mkv', '.webm'))),
                    None
                )

                if not video_file:
                    shutil.rmtree(temp_dir)  # Clean up in case of failure
                    return Response(
                        {"error": "Video not found after download."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                def file_iterator(file_path, chunk_size=8192):
                    with open(file_path, 'rb') as f:
                        while chunk := f.read(chunk_size):
                            yield chunk

                response = StreamingHttpResponse(
                    file_iterator(video_file), content_type='application/octet-stream'
                )
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(video_file)}"'

                response['X-Sendfile-Cleanup'] = temp_dir  # Custom header for cleanup

                def cleanup():
                    shutil.rmtree(temp_dir)

                response.close = cleanup

                return response

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)