"""
Clinical data models for vital signs, lab results, and imaging.
"""
from django.db import models
from core.models import AuditableModel
from patients.models import Patient


class VitalSigns(AuditableModel):
    """
    Patient vital signs measurements.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    measurement_date = models.DateTimeField()
    
    # Vital signs
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_unit = models.CharField(max_length=1, choices=[('F', 'Fahrenheit'), ('C', 'Celsius')], default='F')
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True)
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True)
    oxygen_saturation = models.PositiveIntegerField(null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in inches
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in pounds
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'clinical_data_vital_signs'
        ordering = ['-measurement_date']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.measurement_date.date()}"