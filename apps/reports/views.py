from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.reports.services import get_monthly_summary


@extend_schema(
    parameters=[
        OpenApiParameter(name="year", type=int, required=True, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="month", type=int, required=True, location=OpenApiParameter.QUERY),
    ],
    responses={200: OpenApiResponse(description="Monthly financial summary.")},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_summary(request):
    year = request.query_params.get("year")
    month = request.query_params.get("month")

    if not year or not month:
        return Response(
            {"detail": "Query parameters 'year' and 'month' are required."},
            status=400,
        )

    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return Response(
            {"detail": "Query parameters 'year' and 'month' must be integers."},
            status=400,
        )

    if month < 1 or month > 12:
        return Response(
            {"detail": "Query parameter 'month' must be between 1 and 12."},
            status=400,
        )

    return Response(get_monthly_summary(user=request.user, year=year, month=month))
