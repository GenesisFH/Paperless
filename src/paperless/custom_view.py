# src/paperless/custom_views.py

#Apis anteriores
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,  AllowAny
from rest_framework.response import Response
from django.db.models import Count, Sum
from documents.models import Document
from django.db.models.functions import TruncDate
from django.apps import apps
import os
from collections import Counter



@api_view(['GET'])
@permission_classes([AllowAny])
def documentos_por_area_y_usuario(request):
    """
    Devuelve número de documentos agrupados por día, área (correspondent) y usuario.
    """
    datos = (
        Document.objects
        .annotate(date=TruncDate('created'))
        .values('date', 'owner__username', 'correspondent__name')
        .annotate(total=Count('id'))
        .order_by('date')
    )
    return Response(list(datos))



@api_view(['GET'])
@permission_classes([AllowAny])
def file_extensions(request):
    Document = apps.get_model('documents', 'Document')
    documents = Document.objects.all()
    extensions = [os.path.splitext(doc.filename)[1].lower() for doc in documents if doc.filename]
    count_ext = Counter(extensions)
    
    data = [
        {"extension": ext or "(sin extensión)", "count": count}
        for ext, count in count_ext.items()
    ]
    return Response(data)
