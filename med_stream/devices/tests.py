from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.enums import UserRole
from accounts.models import CustomUser
from devices.enums import DeviceStatus, DeviceType, LogType, OrientationChoices
from devices.models import Device, DeviceHealth, DeviceLog
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


class DeviceNextCommandTests(TestCase):
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
        self.device = Device.objects.create(
            name="TV 1",
            facility=self.facility,
            block=self.block,
            floor=self.floor,
            device_type=DeviceType.TV,
            orientation=OrientationChoices.LANDSCAPE,
            ip_address="192.168.1.10",
        )
        self.url = reverse("device_next_command", kwargs={"device_id": self.device.id})

    def create_command(self, command, executed=False):
        return DeviceLog.objects.create(
            device=self.device,
            log_type=LogType.INFO,
            message=f"{command} command issued",
            metadata={
                "command": command,
                "media": {
                    "media_type": "IMAGE",
                    "file_url": "/media/test.jpg",
                },
                "executed": executed,
            },
        )

    def test_returns_pending_play_command(self):
        command = self.create_command("PLAY")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["command_id"], str(command.id))
        self.assertEqual(response.json()["payload"]["command"], "PLAY")

    def test_restores_latest_executed_play_command(self):
        command = self.create_command("PLAY", executed=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["command_id"], str(command.id))
        self.assertEqual(response.json()["payload"]["command"], "PLAY")

    def test_returns_pending_stop_command(self):
        command = self.create_command("STOP")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["command_id"], str(command.id))
        self.assertEqual(response.json()["payload"]["command"], "STOP")

    def test_does_not_restore_after_executed_stop(self):
        self.create_command("PLAY", executed=True)
        self.create_command("STOP", executed=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["command"])
