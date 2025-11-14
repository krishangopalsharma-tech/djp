# Path: backend/sections/serializers.py
from rest_framework import serializers
from .models import Section, SubSection, Asset
from depots.models import Depot

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'name', 'quantity', 'unit', 'subsection', 'created_at', 'updated_at']

class SubSectionSerializer(serializers.ModelSerializer):
    assets = AssetSerializer(many=True, read_only=True)
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)

    class Meta:
        model = SubSection
        fields = ['id', 'name', 'section', 'assets', 'asset_count', 'created_at', 'updated_at']

class SectionSerializer(serializers.ModelSerializer):
    subsections = SubSectionSerializer(many=True, read_only=True)
    subsection_count = serializers.IntegerField(source='subsections.count', read_only=True)
    depot_display = serializers.CharField(source='depot.name', read_only=True)
    depot_code = serializers.CharField(source='depot.code', read_only=True) # Added for display
    depot = serializers.PrimaryKeyRelatedField(queryset=Depot.objects.all()) # For writing

    class Meta:
        model = Section
        fields = ['id', 'name', 'depot', 'depot_display', 'depot_code', 'subsections', 'subsection_count', 'created_at', 'updated_at']
        read_only_fields = ['depot_display', 'depot_code']

# --- Serializers for the Infrastructure Tree View ---

class _AssetTreeSerializer(serializers.ModelSerializer):
    """Lightweight Asset serializer for the tree view."""
    class Meta:
        model = Asset
        fields = ['id', 'name']

class _SubSectionTreeSerializer(serializers.ModelSerializer):
    """Lightweight SubSection serializer for the tree view."""
    assets = _AssetTreeSerializer(many=True, read_only=True)
    class Meta:
        model = SubSection
        fields = ['id', 'name', 'assets']

class _SectionTreeSerializer(serializers.ModelSerializer):
    """Lightweight Section serializer for the tree view."""
    subsections = _SubSectionTreeSerializer(many=True, read_only=True)
    class Meta:
        model = Section
        fields = ['id', 'name', 'subsections']

class _DepotTreeSerializer(serializers.ModelSerializer):
    """Lightweight Depot serializer for the tree view."""
    sections = _SectionTreeSerializer(many=True, read_only=True)
    # We can add stations here if needed by the modal
    
    class Meta:
        model = Depot
        fields = ['id', 'name', 'code', 'sections']