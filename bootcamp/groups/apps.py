from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GroupsConfig(AppConfig):
    name = "bootcamp.groups"
    verbose_name = _("Groups")
