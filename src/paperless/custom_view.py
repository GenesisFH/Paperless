# src/paperless/custom_views.py

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
@permission_classes([IsAuthenticated])
def documentos_por_area_y_usuario(request):
    """
    Devuelve número de documentos agrupados por día, etiqueta (tag) y usuario.
    Si el usuario es superusuario, ve todos los documentos; si no, solo los suyos.
    """
    user = request.user
    documents = Document.objects.all() if user.is_superuser else Document.objects.filter(owner=user)

    datos = (
        documents
        .annotate(date=TruncDate('created'))
        .values('date', 'owner__username', 'tags__name')  # Agrupar por etiqueta
        .annotate(total=Count('id'))
        .order_by('date', 'tags__name')
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



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_documents_sizes(request):
    Document = apps.get_model('documents', 'Document')
    
    
    if request.user.is_superuser:
        documents = Document.objects.all()
    else:
        documents = Document.objects.filter(owner=request.user)

    data = []
    for doc in documents:
        size_kb = None
        if doc.archive_path and os.path.exists(doc.archive_path):
            size_bytes = os.path.getsize(doc.archive_path)
            size_kb = round(size_bytes / 1024, 2)
        data.append({
            "id": doc.id,
            "title": doc.title,
            "size_kb": size_kb,
        })
    
    return Response(data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_total_storage(request):
    Document = apps.get_model('documents', 'Document')
    
    user = request.user

    if request.user.is_superuser:
        documents = Document.objects.all()
    else:
        documents = Document.objects.filter(owner=request.user)

    total_size_bytes = 0
    for doc in documents:
        if doc.archive_path and os.path.exists(doc.archive_path):
            total_size_bytes += os.path.getsize(doc.archive_path)

    total_size_gb = round(total_size_bytes / (1024 ** 3), 3)  # GB con 3 decimales

    data = {
        "user_id": user.id,
        "username": user.username,
        "total_storage_gb":  total_size_gb,
    }

    return Response(data)