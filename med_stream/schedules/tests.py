from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from accounts.models import CustomUser
from facilities.models import Facility
from organizations.models import Organization
from schedules.forms import OPDScheduleForm
from schedules.models import Doctor, DoctorSchedule, OPDRoom


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
