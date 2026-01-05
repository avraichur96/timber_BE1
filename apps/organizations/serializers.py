from rest_framework import serializers
from .models import Organization, Subscription, OrganizationMember, Customer, Project, EstimateHeader, Product, EstimateDetail, JobCard


class FlexibleDateField(serializers.DateField):
    def to_internal_value(self, data):
        if data == "" or data is None:
            return None
        return super().to_internal_value(data)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "description",
            "created_by",
            "created_at",
            "updated_at",
            "is_active",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")


class SubscriptionSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = Subscription
        fields = (
            "id",
            "organization",
            "organization_name",
            "plan_name",
            "has_expired",
            "started_at",
            "updated_at",
        )
        read_only_fields = ("id", "started_at", "updated_at")


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(
        source="user.get_full_name", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = OrganizationMember
        fields = (
            "id",
            "organization",
            "organization_name",
            "user",
            "user_email",
            "user_name",
            "role",
            "joined_at",
            "is_active",
        )
        read_only_fields = ("id", "joined_at")


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            "id",
            "name",
            "email",
            "phone_number",
            "address",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_phone_number(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only numerical characters.")
        return value


class ProjectSerializer(serializers.ModelSerializer):
    customerId = serializers.UUIDField(source="customer.id", read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "customerId",
            "customer",
            "name",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

class ProjectPostSerializer(serializers.ModelSerializer):
    customerId = serializers.UUIDField(write_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "customerId",
            "name",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        customer_id = validated_data.pop('customerId')
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Customer with this ID does not exist.")
        
        return Project.objects.create(customer=customer, **validated_data)


class EstimateHeaderSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = EstimateHeader
        fields = (
            "id",
            "project",
            "project_name",
            "status",
            "transport_handling_cost",
            "discount",
            "approximate_tax",
            "estimated_total",
            "description",
            "additional_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class EstimateHeaderPostSerializer(serializers.ModelSerializer):
    projectId = serializers.UUIDField(write_only=True)

    class Meta:
        model = EstimateHeader
        fields = (
            "id",
            "projectId",
            "status",
            "transport_handling_cost",
            "discount",
            "approximate_tax",
            "estimated_total",
            "description",
            "additional_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        project_id = validated_data.pop('projectId')
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project with this ID does not exist.")
        
        return EstimateHeader.objects.create(project=project, **validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class EstimateDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = EstimateDetail
        fields = (
            "id",
            "product",
            "product_name",
            "overall_length",
            "overall_breadth",
            "overall_height",
            "labor_charges",
            "polishing_charges",
            "component_name",
            "component_length",
            "component_breadth",
            "component_thickness",
            "component_cft",
            "component_cost_per_cft",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class EstimateDetailCreateSerializer(serializers.ModelSerializer):
    productId = serializers.UUIDField(write_only=True)

    class Meta:
        model = EstimateDetail
        fields = (
            "productId",
            "overall_length",
            "overall_breadth",
            "overall_height",
            "labor_charges",
            "polishing_charges",
            "component_name",
            "component_length",
            "component_breadth",
            "component_thickness",
            "component_cft",
            "component_cost_per_cft",
        )

    def validate_productId(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product with this ID does not exist.")
        return value

    def create(self, validated_data, estimate_header):
        product_id = validated_data.pop('productId')
        product = Product.objects.get(id=product_id)
        return EstimateDetail.objects.create(
            estimate_header=estimate_header,
            product=product,
            **validated_data
        )


class EstimateHeaderWithDetailsSerializer(serializers.ModelSerializer):
    projectId = serializers.UUIDField(write_only=True)
    details = EstimateDetailCreateSerializer(many=True, write_only=True)

    class Meta:
        model = EstimateHeader
        fields = (
            "id",
            "projectId",
            "status",
            "transport_handling_cost",
            "discount",
            "approximate_tax",
            "estimated_total",
            "description",
            "additional_notes",
            "details",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_projectId(self, value):
        if not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError("Project with this ID does not exist.")
        return value

    def validate_details(self, value):
        if not value:
            raise serializers.ValidationError("At least one estimate detail is required.")
        
        for detail in value:
            if detail.get('component_cft', 0) < 0:
                raise serializers.ValidationError("Component CFT must be greater than 0.")
            if detail.get('component_cost_per_cft', 0) < 0:
                raise serializers.ValidationError("Component cost per CFT must be greater than 0.")
        
        return value

    def create(self, validated_data):
        project_id = validated_data.pop('projectId')
        details_data = validated_data.pop('details')
        
        project = Project.objects.get(id=project_id)
        estimate_header = EstimateHeader.objects.create(project=project, **validated_data)
        
        # Create estimate details
        detail_serializer = EstimateDetailCreateSerializer()
        for detail_data in details_data:
            detail_serializer.create(detail_data, estimate_header)
        
        return estimate_header


class EstimateHeaderWithDetailsReadSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    details = EstimateDetailSerializer(source="estimate_details", many=True, read_only=True)

    class Meta:
        model = EstimateHeader
        fields = (
            "id",
            "project",
            "project_name",
            "status",
            "transport_handling_cost",
            "discount",
            "approximate_tax",
            "estimated_total",
            "description",
            "additional_notes",
            "details",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class EstimateHeaderUpdateSerializer(serializers.ModelSerializer):
    projectId = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = EstimateHeader
        fields = (
            "id",
            "projectId",
            "status",
            "transport_handling_cost",
            "discount",
            "approximate_tax",
            "estimated_total",
            "description",
            "additional_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_projectId(self, value):
        if value and not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError("Project with this ID does not exist.")
        return value

    def update(self, instance, validated_data):
        project_id = validated_data.pop('projectId', None)
        if project_id:
            project = Project.objects.get(id=project_id)
            instance.project = project
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class EstimateDetailUpdateSerializer(serializers.ModelSerializer):
    productId = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = EstimateDetail
        fields = (
            "id",
            "productId",
            "overall_length",
            "overall_breadth",
            "overall_height",
            "labor_charges",
            "polishing_charges",
            "component_name",
            "component_length",
            "component_breadth",
            "component_thickness",
            "component_cft",
            "component_cost_per_cft",
        )

    def validate_productId(self, value):
        if value and not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product with this ID does not exist.")
        return value


class EstimateHeaderWithDetailsUpdateSerializer(serializers.ModelSerializer):
    projectId = serializers.UUIDField(write_only=True, required=False)
    details = EstimateDetailUpdateSerializer(many=True, required=False)

    class Meta:
        model = EstimateHeader
        fields = (
            "id",
            "projectId",
            "status",
            "transport_handling_cost",
            "discount",
            "approximate_tax",
            "estimated_total",
            "description",
            "additional_notes",
            "details",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_projectId(self, value):
        if value and not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError("Project with this ID does not exist.")
        return value

    def validate_details(self, value):
        if value is not None:
            for detail in value:
                if detail.get('component_cft', 0) < 0:
                    raise serializers.ValidationError("Component CFT must be greater than 0.")
                if detail.get('component_cost_per_cft', 0) < 0:
                    raise serializers.ValidationError("Component cost per CFT must be greater than 0.")
        return value

    def update(self, instance, validated_data):
        project_id = validated_data.pop('projectId', None)
        details_data = validated_data.pop('details', None)
        
        # Update project if provided
        if project_id:
            project = Project.objects.get(id=project_id)
            instance.project = project
        
        # Update header fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update details if provided
        if details_data is not None:
            # Remove existing details
            instance.estimate_details.all().delete()
            
            # Create new details
            for detail_data in details_data:
                product_id = detail_data.pop('productId', None)
                if product_id:
                    product = Product.objects.get(id=product_id)
                else:
                    # Use existing product if not provided
                    continue
                
                EstimateDetail.objects.create(
                    estimate_header=instance,
                    product=product,
                    **detail_data
                )
        
        return instance


class JobCardSerializer(serializers.ModelSerializer):
    estimate_header_name = serializers.CharField(source="estimate_header.project.name", read_only=True)
    measurements = serializers.SerializerMethodField()
    item_name = serializers.CharField(source="product.name", read_only=True, default='')

    class Meta:
        model = JobCard
        fields = (
            "id",
            "estimate_header",
            "estimate_header_name",
            "job_name",
            "description",
            "wood_species",
            "status",
            "location",
            "people",
            "carpenter_charges",
            "start_date",
            "end_date",
            "due_date",
            "measurements", 
            "item_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_measurements(self, obj):
        """Get measurements from estimate details using product reference"""
        if not obj.product:
            return []
        
        # Get estimate details for this job card's estimate header and product
        estimate_details = EstimateDetail.objects.filter(
            estimate_header=obj.estimate_header,
            product=obj.product
        )
        
        measurements = []
        for detail in estimate_details:
            measurements.append({
                "id": str(detail.id),
                "componentName": detail.component_name or "",
                "length": detail.component_length or 0,
                "breadth": detail.component_breadth or 0,
                "thickness": detail.component_thickness or 0,
                "cft": detail.component_cft or 0,
                "cost_per_cft": detail.component_cost_per_cft or 0,
                "labor_charges": detail.labor_charges or 0,
                "polishing_charges": detail.polishing_charges or 0,
                "overall_length": detail.overall_length or 0,
                "overall_breadth": detail.overall_breadth or 0,
                "overall_height": detail.overall_height or 0,
            })
        return measurements


class JobCardPostSerializer(serializers.ModelSerializer):
    estimateHeaderId = serializers.UUIDField(write_only=True)
    product = serializers.UUIDField(
        write_only=True,
        required=True,
        allow_null=True,
        help_text="Product ID associated with this job card"
    )
    item_name = serializers.CharField(source="product.name", read_only=True)
    start_date = FlexibleDateField(required=False, allow_null=True)
    end_date = FlexibleDateField(required=False, allow_null=True)
    due_date = FlexibleDateField(required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override date fields to handle empty strings
        self.fields['start_date'].input_formats = ['%m/%d/%Y', '%Y-%m-%d']
        self.fields['end_date'].input_formats = ['%m/%d/%Y', '%Y-%m-%d']
        self.fields['due_date'].input_formats = ['%m/%d/%Y', '%Y-%m-%d']
        
        # Debug: Print input formats to verify they're set correctly
        print(f"DEBUG: start_date input_formats: {self.fields['start_date'].input_formats}")
        print(f"DEBUG: end_date input_formats: {self.fields['end_date'].input_formats}")
        print(f"DEBUG: due_date input_formats: {self.fields['due_date'].input_formats}") 

    class Meta:
        model = JobCard
        fields = (
            "id",
            "estimateHeaderId",
            "job_name",
            "description",
            "wood_species",
            "status",
            "location",
            "people",
            "carpenter_charges",
            "start_date",
            "end_date",
            "due_date",
            "item_name",
            "created_at",
            "updated_at",
            "product",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_start_date(self, value):
        if value == "" or value is None:
            return None
        try:
            return serializers.DateField(input_formats=['%m/%d/%Y', '%Y-%m-%d']).to_internal_value(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Invalid date format. Please use MM/DD/YYYY or YYYY-MM-DD.")

    def validate_end_date(self, value):
        if value == "" or value is None:
            return None
        try:
            return serializers.DateField(input_formats=['%m/%d/%Y', '%Y-%m-%d']).to_internal_value(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Invalid date format. Please use MM/DD/YYYY or YYYY-MM-DD.")

    def validate_people(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("People field must be a list.")
        
        for person in value:
            if not isinstance(person, dict):
                raise serializers.ValidationError("Each person must be a JSON object.")
            
            if 'name' not in person:
                raise serializers.ValidationError("Each person must have a 'name' field.")
            
            if not isinstance(person['name'], str):
                raise serializers.ValidationError("Person name must be a string.")
            
            if 'is_carpenter' in person and not isinstance(person['is_carpenter'], bool):
                raise serializers.ValidationError("Person 'is_carpenter' field must be a boolean.")
        
        return value

    def create(self, validated_data):
        estimate_header_id = validated_data.pop('estimateHeaderId')
        product_id = validated_data.pop('product', None)
        
        try:
            estimate_header = EstimateHeader.objects.get(id=estimate_header_id)
        except EstimateHeader.DoesNotExist:
            raise serializers.ValidationError("EstimateHeader with this ID does not exist.")
        
        # Get product if provided
        product = None
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError("Product with this ID does not exist.")
        
        # Create job card with product
        job_card = JobCard.objects.create(
            estimate_header=estimate_header, 
            product=product, 
            **validated_data
        )
        
        return job_card