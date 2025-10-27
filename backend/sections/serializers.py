# Path: backend/sections/serializers.py
from rest_framework import serializers
from .models import Section, SubSection, Asset
from depots.models import Depot # Import for write operations

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
    # Include depot details for display purposes, but use PrimaryKeyRelatedField for writing
    depot_display = serializers.CharField(source='depot.name', read_only=True)
    depot = serializers.PrimaryKeyRelatedField(queryset=Depot.objects.all()) # For creating/updating

    class Meta:
        model = Section
        fields = ['id', 'name', 'depot', 'depot_display', 'subsections', 'subsection_count', 'created_at', 'updated_at']
        read_only_fields = ['depot_display'] # Prevent writing to display field
