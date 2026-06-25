from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.enums import UserRole
from accounts.models import CustomUser
from devices.enums import DeviceStatus, DeviceType, OrientationChoices
from devices.models import Device, DeviceHealth
from facilities.models import Block, Facility, Floor
from organizations.models import Organization


class DeviceListViewTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Org",
            organization_type="HOSPITAL",
        )
        self.facility = Facility.objects.create(
            name="Test Facility",
            organization=self.organization,
        )
        self.block = Block.objects.create(
            facility=self.facility,
            name="Block A",
        )
        self.floor = Floor.objects.create(
            block=self.block,
            name="Floor 1",
        )
        self.user = CustomUser.objects.create_user(
            phone_number="9999999999",
            password="password123",
            organization=self.organization,
            role=UserRole.ADMIN,
        )
        self.device = Device.objects.create(
            name="TV 1",
            facility=self.facility,
            block=self.block,
            floor=self.floor,
            device_type=DeviceType.TV,
            orientation=OrientationChoices.LANDSCAPE,
            ip_address="192.168.1.10",
        )
        self.health = DeviceHealth.objects.create(
            device=self.device,
            status=DeviceStatus.OFFLINE,
            last_seen_at=timezone.now() - timedelta(seconds=10),
        )

    def test_device_list_renders_fresh_health_status(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("devices"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, DeviceStatus.ONLINE)
        self.health.refresh_from_db()
        self.assertEqual(self.health.status, DeviceStatus.ONLINE)
