from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone

from accounts.models import CustomUser
from facilities.models import Facility
from organizations.models import Organization
from schedules.forms import OPDScheduleForm
from schedules.models import Doctor, DoctorSchedule, OPDRoom, OPDSchedule
from django.urls import reverse


class OPDScheduleFormAvailabilityTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-organization",
            registration_number="REG-001",
            email="org@example.com",
            phone_number="9000000001",
        )
        self.facility = Facility.objects.create(
            name="Main Facility",
            organization=self.organization,
            phone_number="9000000002",
        )
        self.user = CustomUser.objects.create(
            phone_number="9000000003",
            role="STAFF",
            organization=self.organization,
            facility=self.facility,
        )
        self.doctor = Doctor.objects.create(
            name="Dr. Smith",
            organization=self.organization,
            facility=self.facility,
        )
        self.opd_room = OPDRoom.objects.create(
            name="OPD Room 1",
            organization=self.organization,
            facility=self.facility,
        )

    def _build_post_data(self, doctor, selected_day):
        return {
            "doctor": str(doctor.id),
            "opd_room": str(self.opd_room.id),
            "day_of_week": [selected_day],
            "start_time": "09:00",
            "end_time": "10:00",
            "is_available": "on",
        }

    def test_opd_form_excludes_doctor_out_today(self):
        today = timezone.now().date()
        DoctorSchedule.objects.create(
            doctor=self.doctor,
            start_date=today,
            end_date=today,
            reason="Annual leave",
        )

        form = OPDScheduleForm(
            user=self.user,
            data=self._build_post_data(self.doctor, today.weekday()),
        )

        self.assertFalse(
            form.fields["doctor"].queryset.filter(pk=self.doctor.pk).exists()
        )

    def test_opd_form_excludes_doctor_out_on_selected_recurring_day(self):
        today = timezone.now().date()
        selected_date = today + timedelta(days=1)
        selected_day = selected_date.weekday()

        DoctorSchedule.objects.create(
            doctor=self.doctor,
            start_date=selected_date,
            end_date=selected_date,
            reason="Conference",
        )

        form = OPDScheduleForm(
            user=self.user,
            data=self._build_post_data(self.doctor, selected_day),
        )

        self.assertFalse(
            form.fields["doctor"].queryset.filter(pk=self.doctor.pk).exists()
        )

    def test_opd_form_invalid_without_doctor_does_not_raise(self):
        form = OPDScheduleForm(user=self.user, data={})

        self.assertFalse(form.is_valid())
        self.assertIn("doctor", form.errors)


class SchedulesViewTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-organization",
            registration_number="REG-002",
            email="org2@example.com",
            phone_number="9000000004",
        )
        self.facility = Facility.objects.create(
            name="Secondary Facility",
            organization=self.organization,
            phone_number="9000000005",
        )
        self.user = CustomUser.objects.create_user(
            phone_number="9000000006",
            password="password123",
            organization=self.organization,
            role="ADMIN",
        )
        self.doctor = Doctor.objects.create(
            name="Dr. Past",
            organization=self.organization,
            facility=self.facility,
        )

    def test_schedules_view_excludes_past_doctor_schedules(self):
        today = timezone.localdate()
        DoctorSchedule.objects.create(
            doctor=self.doctor,
            start_date=today - timedelta(days=10),
            end_date=today - timedelta(days=1),
            reason="Finished leave",
        )
        active_schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            start_date=today,
            end_date=today + timedelta(days=3),
            reason="Current leave",
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("schedules"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["doctor_schedules"],
            [active_schedule],
            transform=lambda item: item,
        )

    def test_schedules_view_excludes_past_opd_schedules(self):
        today = timezone.localdate()
        current_time = timezone.localtime().time()
        current_dt = datetime.combine(today, current_time)
        past_end_time = (current_dt - timedelta(minutes=1)).time()
        future_end_time = (current_dt + timedelta(minutes=1)).time()
        start_time = (current_dt - timedelta(hours=1)).time()

        past_schedule = OPDSchedule.objects.create(
            doctor=self.doctor,
            opd_room=OPDRoom.objects.create(
                name="Room Past",
                organization=self.organization,
                facility=self.facility,
            ),
            day_of_week=today.weekday(),
            start_time=start_time,
            end_time=past_end_time,
            is_available=True,
        )
        active_schedule = OPDSchedule.objects.create(
            doctor=self.doctor,
            opd_room=OPDRoom.objects.create(
                name="Room Active",
                organization=self.organization,
                facility=self.facility,
            ),
            day_of_week=today.weekday(),
            start_time=start_time,
            end_time=future_end_time,
            is_available=True,
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("schedules"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["opd_schedules"],
            [active_schedule],
            transform=lambda item: item,
        )

    def test_schedules_view_includes_date_based_opd_schedule(self):
        today = timezone.localdate()

        dated_schedule = OPDSchedule.objects.create(
            doctor=self.doctor,
            opd_date=today,
            opd_room=OPDRoom.objects.create(
                name="Room Date",
                organization=self.organization,
                facility=self.facility,
            ),
            start_time=(timezone.localtime() - timedelta(hours=1)).time(),
            end_time=(timezone.localtime() + timedelta(hours=1)).time(),
            is_available=True,
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("schedules"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, today.strftime("%d %b %Y"))
        self.assertQuerySetEqual(
            response.context["opd_schedules"],
            [dated_schedule],
            transform=lambda item: item,
        )
