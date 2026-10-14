"""Custom form fields and form mixins."""

import uuid

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from nautobot.apps.forms import APISelectMultiple


class ReadOnlyHiddenInput(forms.MultipleHiddenInput):
    """Render nothing and read nothing from the request, for a field another form field fills in clean()."""

    def render(self, name, value, attrs=None, renderer=None):
        """Render nothing."""
        return ""

    def value_from_datadict(self, data, files, name):
        """Read nothing."""
        return []


class ManagedLocallyGroupFormMixin:
    """Refuse members on a group whose status is Managed Locally."""

    def clean(self):
        """Check the submitted status and members together, since both may change in one edit."""
        super().clean()
        model = self._meta.model
        model.validate_managed_members(
            self.cleaned_data.get("status"), {field: self.cleaned_data.get(field) for field in model.members_fields}
        )
        return self.cleaned_data


class GroupedObjectsField(forms.MultipleChoiceField):
    """A picker whose values are `object:<pk>` or `group:<pk>`, searched through the grouped objects API.

    ObjectOrGroupFormMixin checks the values against what the user may view, so the field itself accepts any value.
    """

    def valid_value(self, value):
        """Leave validation to ObjectOrGroupFormMixin.clean()."""
        return True


class ObjectOrGroupFormMixin:
    """Show one picker per rule field that searches objects and their groups together, e.g. Zones and Zone Groups.

    The model keeps separate fields such as `source_zones` and `source_zone_groups`. Those stay on the form, so Nautobot
    still limits them to what the user may view, but they are hidden and filled from one `<field>_and_groups` picker.
    """

    # Suffix of an object field, mapped to the suffix of its group field and the grouped objects API kind the picker
    # searches.
    GROUPED_SUFFIXES = {
        "zones": ("zone_groups", "zones"),
        "addresses": ("address_groups", "addresses"),
        "address_objects": ("address_object_groups", "addresses"),
        "services": ("service_groups", "services"),
        "users": ("user_groups", "users"),
        "applications": ("application_groups", "applications"),
    }
    PREFIXES = ("group:", "object:")

    def combine_grouped_fields(self):
        """Replace each object and group field pair with one combined picker in the object field's position."""
        self.grouped_pairs = {}
        for name in self.fields:
            for suffix, (group_suffix, kind) in self.GROUPED_SUFFIXES.items():
                group_name = name.removesuffix(suffix) + group_suffix
                if name.endswith(suffix) and group_name in self.fields:
                    self.grouped_pairs[f"{name}_and_groups"] = (name, group_name, kind)
        fields = {}
        for name, field in self.fields.items():
            if f"{name}_and_groups" in self.grouped_pairs:
                fields[f"{name}_and_groups"] = self._combined_field(f"{name}_and_groups")
            fields[name] = field
        for objects_name, groups_name, _kind in self.grouped_pairs.values():
            for name in (objects_name, groups_name):
                fields[name].widget = ReadOnlyHiddenInput()
        self.fields = fields

    def _combined_field(self, combined_name):
        objects_name, groups_name, kind = self.grouped_pairs[combined_name]
        widget = APISelectMultiple()
        widget.attrs["data-url"] = reverse(
            "plugins-api:nautobot_firewall_models-api:grouped-objects", kwargs={"kind": kind}
        )
        model = self.fields[objects_name].queryset.model
        # Only the selected options are rendered; the rest are searched as the user types. The choices are read when
        # the form renders, after Nautobot has restricted the querysets to what the user may view.
        field = GroupedObjectsField(
            choices=lambda: self._selected_choices(combined_name),
            required=False,
            label=objects_name.replace("_", " ").title(),
            help_text=f"{model._meta.verbose_name_plural.title()} and their groups.",
            widget=widget,
        )
        selected = [f"group:{getattr(i, 'pk', i)}" for i in self.initial.get(groups_name) or []]
        selected += [f"object:{getattr(i, 'pk', i)}" for i in self.initial.get(objects_name) or []]
        self.initial[combined_name] = selected
        return field

    def _selected_values(self, combined_name):
        if self.is_bound:
            return self.fields[combined_name].widget.value_from_datadict(
                self.data, self.files, self.add_prefix(combined_name)
            )
        return self.initial.get(combined_name) or []

    def _split_values(self, combined_name, values):
        """Return the selected objects and groups, and whether every value was one the user may select."""
        objects_name, groups_name, _kind = self.grouped_pairs[combined_name]
        selected = {}
        valid = True
        for prefix, name in (("object:", objects_name), ("group:", groups_name)):
            pks = set()
            for value in values:
                if value.startswith(prefix):
                    try:
                        pks.add(uuid.UUID(value.removeprefix(prefix)))
                    except ValueError:
                        valid = False
            selected[name] = self.fields[name].queryset.filter(pk__in=pks)
            valid = valid and selected[name].count() == len(pks)
        valid = valid and all(value.startswith(self.PREFIXES) for value in values)
        return selected, valid

    def _selected_choices(self, combined_name):
        selected, _valid = self._split_values(combined_name, self._selected_values(combined_name))
        objects_name, groups_name, _kind = self.grouped_pairs[combined_name]
        return [(f"group:{i.pk}", str(i)) for i in selected[groups_name]] + [
            (f"object:{i.pk}", str(i)) for i in selected[objects_name]
        ]

    def add_error(self, field, error):
        """Show errors raised for a hidden object or group field on the combined picker that sets it."""
        combined = {
            name: combined_name
            for combined_name, (objects_name, groups_name, _kind) in getattr(self, "grouped_pairs", {}).items()
            for name in (objects_name, groups_name)
        }
        if field is None and hasattr(error, "error_dict"):
            errors = {}
            for name, messages in error.error_dict.items():
                errors.setdefault(combined.get(name, name), []).extend(messages)
            error = ValidationError(errors)
        else:
            field = combined.get(field, field)
        super().add_error(field, error)

    def clean(self):
        """Split each combined picker back into its object and group fields."""
        super().clean()
        for combined_name in self.grouped_pairs:
            values = self.cleaned_data.get(combined_name)
            if values is None:
                continue
            selected, valid = self._split_values(combined_name, values)
            if not valid:
                self.add_error(combined_name, "Select a valid choice.")
                continue
            self.cleaned_data.update(selected)
        return self.cleaned_data
