from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import TextRequestSerializer, TextResponseSerializer
from .services.ollama import fix_with_ollama
from .services.precleaner import derive_book_hint

class TextFixerView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        req = TextRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        raw = req.validated_data["text"]
        folder = req.validated_data.get("folder", "")
        filename = req.validated_data.get("filename", "")

        hint = derive_book_hint(folder, filename)
        fixed = fix_with_ollama(raw, book_hint=hint)

        return Response(TextResponseSerializer({"text": fixed}).data, status=200)