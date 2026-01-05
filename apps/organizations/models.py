from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.core.validators import MinValueValidator

User = get_user_model()


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_organizations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "organizations"
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan_name = models.CharField(max_length=100)
    has_expired = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscriptions"
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.plan_name}"


class OrganizationMember(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organization_memberships"
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="member"
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "organization_members"
        verbose_name = "Organization Member"
        verbose_name_plural = "Organization Members"
        unique_together = ["organization", "user"]
        ordering = ["role", "joined_at"]

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class EstimateHeader(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="estimate_headers"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft"
    )
    transport_handling_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    discount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    approximate_tax = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    estimated_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "estimate_headers"
        verbose_name = "Estimate Header"
        verbose_name_plural = "Estimate Headers"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Estimate for {self.project.name} - {self.get_status_display()}"


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["name"]

    def __str__(self):
        return self.name


class EstimateDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estimate_header = models.ForeignKey(
        EstimateHeader, on_delete=models.CASCADE, related_name="estimate_details"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="estimate_details"
    )
    
    # Overall dimensions
    overall_length = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    overall_breadth = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    overall_height = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Charges
    labor_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    polishing_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Component details
    component_name = models.CharField(max_length=255)
    component_length = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    component_breadth = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    component_thickness = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    component_cft = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    component_cost_per_cft = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "estimate_details"
        verbose_name = "Estimate Detail"
        verbose_name_plural = "Estimate Details"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.component_name} - {self.estimate_header}"


class JobCard(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estimate_header = models.ForeignKey(
        EstimateHeader, on_delete=models.CASCADE, related_name="job_cards"
    )
    job_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    wood_species = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    location = models.TextField(blank=True, null=True)
    people = models.JSONField(default=list, blank=True)  # Text array field
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="job_cards",
        help_text="Product associated with this job card"
    )
    carpenter_charges = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "job_cards"
        verbose_name = "Job Card"
        verbose_name_plural = "Job Cards"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.job_name} - {self.get_status_display()}"
