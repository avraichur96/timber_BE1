from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

from .models import Organization, Subscription, OrganizationMember, Customer, Project, EstimateHeader, Product, EstimateDetail, JobCard
from .exceptions import log_view_errors
from .serializers import (
    OrganizationSerializer,
    SubscriptionSerializer,
    OrganizationMemberSerializer,
    CustomerSerializer,
    ProjectSerializer,
    ProjectPostSerializer,
    EstimateHeaderSerializer,
    EstimateHeaderPostSerializer,
    EstimateHeaderWithDetailsSerializer,
    EstimateHeaderWithDetailsReadSerializer,
    EstimateHeaderUpdateSerializer,
    EstimateHeaderWithDetailsUpdateSerializer,
    ProductSerializer,
    JobCardSerializer,
    JobCardPostSerializer,
)


@extend_schema(
    summary="List organizations",
    responses={200: OrganizationSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def organization_list(request):
    try:
        organizations = Organization.objects.filter(
            members__user=request.user, members__is_active=True
        ).distinct()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in organization_list: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "error_detail": str(e)
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Create organization",
    request=OrganizationSerializer,
    responses={201: OrganizationSerializer},
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@log_view_errors("organization_create")
def organization_create(request):
    try:
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            organization = serializer.save(created_by=request.user)

            # Add creator as owner
            OrganizationMember.objects.create(
                organization=organization, user=request.user, role="owner"
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in organization_create: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "error_detail": str(e)
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Get organization details",
    responses={200: OrganizationSerializer},
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def organization_detail(request, pk):
    organization = get_object_or_404(
        Organization, pk=pk, members__user=request.user
    )
    serializer = OrganizationSerializer(organization)
    return Response(serializer.data)


@extend_schema(
    summary="Update organization",
    request=OrganizationSerializer,
    responses={200: OrganizationSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def organization_update(request, pk):
    try:
        organization = get_object_or_404(
            Organization,
            pk=pk,
            members__user=request.user,
            members__role__in=["owner", "admin"],
        )
        serializer = OrganizationSerializer(
            organization, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in organization_update: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "error_detail": str(e)
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="List subscriptions",
    responses={200: SubscriptionSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def subscription_list(request):
    subscriptions = Subscription.objects.filter(
        organization__members__user=request.user,
        organization__members__is_active=True,
    ).select_related("organization")
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Create subscription",
    request=SubscriptionSerializer,
    responses={201: SubscriptionSerializer},
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def subscription_create(request):
    try:
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            # Check if user has permission to create subscription for this
            # organization
            organization = serializer.validated_data["organization"]
            if not OrganizationMember.objects.filter(
                organization=organization,
                user=request.user,
                role__in=["owner", "admin"],
                is_active=True,
            ).exists():
                return Response(
                    {
                        "error": "You do not have permission to create subscriptions for this organization",
                        "error_detail": "User lacks required role (owner/admin) in this organization"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in subscription_create: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "error_detail": str(e)
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="List organization members",
    responses={200: OrganizationMemberSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def organization_members_list(request, pk):
    organization = get_object_or_404(
        Organization, pk=pk, members__user=request.user
    )
    members = OrganizationMember.objects.filter(
        organization=organization, is_active=True
    )
    serializer = OrganizationMemberSerializer(members, many=True)
    return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class CustomerListCreateView(generics.ListCreateAPIView):
    """
    List all customers or create a new customer.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="List customers",
        responses={200: CustomerSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CustomerListCreateView.get: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Create customer",
        request=CustomerSerializer,
        responses={201: CustomerSerializer},
    )
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CustomerListCreateView.post: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class CustomerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a customer instance.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get customer details",
        responses={200: CustomerSerializer},
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CustomerRetrieveUpdateDestroyView.get: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Update customer",
        request=CustomerSerializer,
        responses={200: CustomerSerializer},
    )
    def put(self, request, *args, **kwargs):
        try:
            return super().put(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CustomerRetrieveUpdateDestroyView.put: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Partial update customer",
        request=CustomerSerializer,
        responses={200: CustomerSerializer},
    )
    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CustomerRetrieveUpdateDestroyView.patch: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Delete customer",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CustomerRetrieveUpdateDestroyView.delete: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ProjectListCreateView(generics.ListCreateAPIView):
    """
    List all projects or create a new project.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="List projects",
        responses={200: ProjectSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProjectListCreateView.get: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Create project",
        request=ProjectPostSerializer,
        responses={201: ProjectPostSerializer},
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = ProjectPostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error in ProjectListCreateView.post: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a project instance.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get project details",
        responses={200: ProjectSerializer},
    )
    def get(self, request, *args, **kwargs):
        try:
            serializer = ProjectSerializer(self.get_object())
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in ProjectRetrieveUpdateDestroyView.get: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Update project",
        request=ProjectPostSerializer,
        responses={200: ProjectPostSerializer},
    )
    def put(self, request, *args, **kwargs):
        try:
            serializer = ProjectPostSerializer(self.get_object(), data=request.data)
            return super().put(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProjectRetrieveUpdateDestroyView.put: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Partial update project",
        request=ProjectPostSerializer,
        responses={200: ProjectPostSerializer},
    )
    def patch(self, request, *args, **kwargs):
        try:
            serializer = ProjectPostSerializer(self.get_object(), data=request.data)
            return super().patch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProjectRetrieveUpdateDestroyView.patch: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Delete project",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProjectRetrieveUpdateDestroyView.delete: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class EstimateHeaderListCreateView(generics.ListCreateAPIView):
    """
    List all estimate headers or create a new estimate header.
    """
    queryset = EstimateHeader.objects.select_related('project').prefetch_related('estimate_details')
    serializer_class = EstimateHeaderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="List estimate headers",
        responses={200: EstimateHeaderWithDetailsReadSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        try:
            self.serializer_class = EstimateHeaderWithDetailsReadSerializer
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in EstimateHeaderListCreateView.get: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Create estimate header",
        request=EstimateHeaderWithDetailsSerializer,
        responses={201: EstimateHeaderWithDetailsSerializer},
    )
    def post(self, request, *args, **kwargs):
        try:
            # Check if request contains details data
            if 'details' in request.data:
                serializer = EstimateHeaderWithDetailsSerializer(data=request.data)
            else:
                # Fallback to original serializer for backward compatibility
                serializer = EstimateHeaderPostSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in EstimateHeaderListCreateView.post: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class EstimateHeaderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an estimate header instance.
    """
    queryset = EstimateHeader.objects.all()
    serializer_class = EstimateHeaderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get estimate header details",
        responses={200: EstimateHeaderSerializer},
    )
    def get(self, request, *args, **kwargs):
        try:
            serializer = EstimateHeaderSerializer(self.get_object())
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in EstimateHeaderRetrieveUpdateDestroyView.get: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Update estimate header",
        request=EstimateHeaderPostSerializer,
        responses={200: EstimateHeaderPostSerializer},
    )
    def put(self, request, *args, **kwargs):
        try:
            serializer = EstimateHeaderPostSerializer(self.get_object(), data=request.data)
            return super().put(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in EstimateHeaderRetrieveUpdateDestroyView.put: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Partial update estimate header",
        request=EstimateHeaderUpdateSerializer,
        responses={200: EstimateHeaderWithDetailsReadSerializer},
    )
    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Check if request contains details data
            if 'details' in request.data:
                serializer = EstimateHeaderWithDetailsUpdateSerializer(instance, data=request.data, partial=True)
            else:
                # Fallback to basic update serializer for backward compatibility
                serializer = EstimateHeaderUpdateSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                updated_instance = serializer.save()
                # Return the updated instance with details using the read serializer
                response_serializer = EstimateHeaderWithDetailsReadSerializer(updated_instance)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in EstimateHeaderRetrieveUpdateDestroyView.patch: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Delete estimate header",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in EstimateHeaderRetrieveUpdateDestroyView.delete: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ProductListCreateView(generics.ListCreateAPIView):
    """
    List all products or create a new product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="List products",
        responses={200: ProductSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProductListCreateView.get: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Create product",
        request=ProductSerializer,
        responses={201: ProductSerializer},
    )
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProductListCreateView.post: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a product instance.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get product details",
        responses={200: ProductSerializer},
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProductRetrieveUpdateDestroyView.get: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Update product",
        request=ProductSerializer,
        responses={200: ProductSerializer},
    )
    def put(self, request, *args, **kwargs):
        try:
            return super().put(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProductRetrieveUpdateDestroyView.put: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Partial update product",
        request=ProductSerializer,
        responses={200: ProductSerializer},
    )
    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProductRetrieveUpdateDestroyView.patch: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Delete product",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProductRetrieveUpdateDestroyView.delete: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class JobCardListCreateView(generics.ListCreateAPIView):
    """
    List all job cards or create a new job card.
    """
    queryset = JobCard.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobCardPostSerializer
        return JobCardSerializer

    @extend_schema(
        summary="List job cards",
        responses={200: JobCardSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in JobCardListCreateView.get: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Create job card",
        request=JobCardPostSerializer,
        responses={201: JobCardSerializer},
    )
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in JobCardListCreateView.post: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class JobCardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a job card instance.
    """
    queryset = JobCard.objects.all()
    serializer_class = JobCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return JobCardPostSerializer
        return JobCardSerializer

    @extend_schema(
        summary="Get job card details",
        responses={200: JobCardSerializer},
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in JobCardRetrieveUpdateDestroyView.get: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Update job card",
        request=JobCardPostSerializer,
        responses={200: JobCardSerializer},
    )
    def put(self, request, *args, **kwargs):
        try:
            return super().put(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in JobCardRetrieveUpdateDestroyView.put: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Partial update job card",
        request=JobCardPostSerializer,
        responses={200: JobCardSerializer},
    )
    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in JobCardRetrieveUpdateDestroyView.patch: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Delete job card",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in JobCardRetrieveUpdateDestroyView.delete: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "Internal server error",
                    "error_detail": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
