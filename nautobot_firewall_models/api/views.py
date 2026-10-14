"""API views for nautobot_firewall_models."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from nautobot.apps.api import ModelViewSet, NautobotModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from nautobot_firewall_models import filters, models
from nautobot_firewall_models.api import serializers


class FQDNViewSet(NautobotModelViewSet):
    """FQDN viewset."""

    queryset = models.FQDN.objects.all().prefetch_related("tags")
    serializer_class = serializers.FQDNSerializer
    filterset_class = filters.FQDNFilterSet


class AddressObjectViewSet(NautobotModelViewSet):
    """AddressObject viewset."""

    queryset = models.AddressObject.objects.all().prefetch_related("tags")
    serializer_class = serializers.AddressObjectSerializer
    filterset_class = filters.AddressObjectFilterSet


class AddressObjectGroupViewSet(NautobotModelViewSet):
    """AddressObjectGroup viewset."""

    queryset = models.AddressObjectGroup.objects.all().prefetch_related("tags")
    serializer_class = serializers.AddressObjectGroupSerializer
    filterset_class = filters.AddressObjectGroupFilterSet


class ApplicationObjectViewSet(NautobotModelViewSet):
    """ApplicationObject viewset."""

    queryset = models.ApplicationObject.objects.all().prefetch_related("tags")
    serializer_class = serializers.ApplicationObjectSerializer
    filterset_class = filters.ApplicationObjectFilterSet


class ApplicationObjectGroupViewSet(NautobotModelViewSet):
    """ApplicationObjectGroup viewset."""

    queryset = models.ApplicationObjectGroup.objects.all().prefetch_related("tags")
    serializer_class = serializers.ApplicationObjectGroupSerializer
    filterset_class = filters.ApplicationObjectGroupFilterSet


class ServiceObjectViewSet(NautobotModelViewSet):
    """ServiceObject viewset."""

    queryset = models.ServiceObject.objects.all().prefetch_related("tags")
    serializer_class = serializers.ServiceObjectSerializer
    filterset_class = filters.ServiceObjectFilterSet


class ServiceObjectGroupViewSet(NautobotModelViewSet):
    """ServiceObjectGroup viewset."""

    queryset = models.ServiceObjectGroup.objects.all().prefetch_related("tags")
    serializer_class = serializers.ServiceObjectGroupSerializer
    filterset_class = filters.ServiceObjectGroupFilterSet


class UserObjectViewSet(NautobotModelViewSet):
    """UserObject viewset."""

    queryset = models.UserObject.objects.all().prefetch_related("tags")
    serializer_class = serializers.UserObjectSerializer
    filterset_class = filters.UserObjectFilterSet


class UserObjectGroupViewSet(NautobotModelViewSet):
    """UserObjectGroup viewset."""

    queryset = models.UserObjectGroup.objects.all()
    serializer_class = serializers.UserObjectGroupSerializer
    filterset_class = filters.UserObjectGroupFilterSet


class ZoneViewSet(NautobotModelViewSet):
    """Zone viewset."""

    queryset = models.Zone.objects.all().prefetch_related("tags")
    serializer_class = serializers.ZoneSerializer
    filterset_class = filters.ZoneFilterSet


class ZoneGroupViewSet(NautobotModelViewSet):
    """ZoneGroup viewset."""

    queryset = models.ZoneGroup.objects.all().prefetch_related("tags")
    serializer_class = serializers.ZoneGroupSerializer
    filterset_class = filters.ZoneGroupFilterSet


class PolicyBandViewSet(NautobotModelViewSet):
    """PolicyBand viewset."""

    queryset = models.PolicyBand.objects.all().prefetch_related("tags")
    serializer_class = serializers.PolicyBandSerializer
    filterset_class = filters.PolicyBandFilterSet


class PolicyRuleViewSet(NautobotModelViewSet):
    """PolicyRule viewset."""

    queryset = models.PolicyRule.objects.all().select_related("band").prefetch_related("tags")
    serializer_class = serializers.PolicyRuleSerializer
    filterset_class = filters.PolicyRuleFilterSet


class PolicyViewSet(NautobotModelViewSet):
    """Policy viewset."""

    queryset = models.Policy.objects.all().prefetch_related("tags")
    serializer_class = serializers.PolicySerializer
    filterset_class = filters.PolicyFilterSet


class NATPolicyRuleViewSet(NautobotModelViewSet):
    """NATPolicyRule viewset."""

    queryset = models.NATPolicyRule.objects.all().prefetch_related("tags")
    serializer_class = serializers.NATPolicyRuleSerializer
    filterset_class = filters.NATPolicyRuleFilterSet


class NATPolicyViewSet(NautobotModelViewSet):
    """NATPolicy viewset."""

    queryset = models.NATPolicy.objects.all().prefetch_related("tags")
    serializer_class = serializers.NATPolicySerializer
    filterset_class = filters.NATPolicyFilterSet


###########################
# Through Models
###########################


class PolicyDeviceM2MViewSet(ModelViewSet):
    """PolicyDeviceM2M viewset."""

    queryset = models.PolicyDeviceM2M.objects.all()
    serializer_class = serializers.PolicyDeviceM2MSerializer
    filterset_class = filters.PolicyDeviceM2MFilterSet


class PolicyDynamicGroupM2MViewSet(ModelViewSet):
    """PolicyDynamicGroupM2M viewset."""

    queryset = models.PolicyDynamicGroupM2M.objects.all()
    serializer_class = serializers.PolicyDynamicGroupM2MSerializer
    filterset_class = filters.PolicyDynamicGroupM2MFilterSet


class NATPolicyDeviceM2MViewSet(ModelViewSet):
    """NATPolicyDeviceM2M viewset."""

    queryset = models.NATPolicyDeviceM2M.objects.all()
    serializer_class = serializers.NATPolicyDeviceM2MSerializer
    filterset_class = filters.NATPolicyDeviceM2MFilterSet


class NATPolicyDynamicGroupM2MViewSet(ModelViewSet):
    """NATPolicyDynamicGroupM2M viewset."""

    queryset = models.NATPolicyDynamicGroupM2M.objects.all()
    serializer_class = serializers.NATPolicyDynamicGroupM2MSerializer
    filterset_class = filters.NATPolicyDynamicGroupM2MFilterSet


class GroupedObjectsView(APIView):
    """Search objects and their groups together, for the combined pickers on the rule forms.

    Results are groups first, then objects, each with an `id` of `group:<pk>` or `object:<pk>` and a `group` heading
    that the picker shows them under. Only what the user may view is returned.
    """

    permission_classes = [IsAuthenticated]
    # Kind, mapped to (group model, group filterset) and (object model, object filterset).
    KINDS = {
        "zones": ((models.ZoneGroup, filters.ZoneGroupFilterSet), (models.Zone, filters.ZoneFilterSet)),
        "addresses": (
            (models.AddressObjectGroup, filters.AddressObjectGroupFilterSet),
            (models.AddressObject, filters.AddressObjectFilterSet),
        ),
        "services": (
            (models.ServiceObjectGroup, filters.ServiceObjectGroupFilterSet),
            (models.ServiceObject, filters.ServiceObjectFilterSet),
        ),
        "users": (
            (models.UserObjectGroup, filters.UserObjectGroupFilterSet),
            (models.UserObject, filters.UserObjectFilterSet),
        ),
        "applications": (
            (models.ApplicationObjectGroup, filters.ApplicationObjectGroupFilterSet),
            (models.ApplicationObject, filters.ApplicationObjectFilterSet),
        ),
    }
    MAX_LIMIT = 1000

    @staticmethod
    def _page(sources, offset, limit):
        """Return one page of results, paging through the groups and then the objects as if they were one list."""
        results = []
        for prefix, model, queryset, count in sources:
            if offset >= count:
                offset -= count
                continue
            heading = {"name": model._meta.verbose_name_plural.title()}
            for obj in queryset[offset : offset + limit - len(results)]:
                results.append({"id": f"{prefix}:{obj.pk}", "name": str(obj), "display": str(obj), "group": heading})
            offset = 0
            if len(results) >= limit:
                break
        return results

    @extend_schema(exclude=True)
    def get(self, request, kind):
        """Return one page of groups and objects matching the `q` search."""
        if kind not in self.KINDS:
            raise Http404
        try:
            limit = min(int(request.query_params.get("limit", 50)), self.MAX_LIMIT)
            offset = max(int(request.query_params.get("offset", 0)), 0)
        except ValueError:
            limit, offset = 50, 0
        search = request.query_params.get("q")

        sources = []
        for prefix, (model, filterset) in zip(("group", "object"), self.KINDS[kind]):
            queryset = model.objects.restrict(request.user, "view")
            if search:
                queryset = filterset({"q": search}, queryset).qs
            sources.append((prefix, model, queryset, queryset.count()))
        total = sum(count for *_rest, count in sources)

        results = self._page(sources, offset, limit)

        def page_url(page_offset):
            query = request.query_params.copy()
            query["offset"] = page_offset
            query["limit"] = limit
            return request.build_absolute_uri(f"{request.path}?{query.urlencode()}")

        return Response(
            {
                "count": total,
                "next": page_url(offset + limit) if offset + limit < total else None,
                "previous": page_url(max(offset - limit, 0)) if offset > 0 else None,
                "results": results,
            }
        )
