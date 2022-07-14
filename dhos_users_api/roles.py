from enum import Enum
from functools import lru_cache
from typing import FrozenSet


class UserRole(Enum):
    DBM_CLINICIAN = "DBM Clinician"
    DBM_SUPERCLINICIAN = "DBM Superclinician"
    DEA_COLLECTOR = "DEA Collector"
    EPR_SERVICE_ADAPTER = "EPR Service Adapter"
    GDM_ADMINISTRATOR = "GDM Administrator"
    GDM_CLINICIAN = "GDM Clinician"
    GDM_PATIENT = "GDM Patient"
    GDM_SUPERCLINICIAN = "GDM Superclinician"
    SEND_ADMINISTRATOR = "SEND Administrator"
    SEND_CLINICIAN = "SEND Clinician"
    SEND_ENTRY_CLINICIAN = "SEND Entry Clinician"
    SEND_ENTRY_DEVICE = "SEND Entry Device"
    SEND_SUPERCLINICIAN = "SEND Superclinician"
    SYSTEM = "System"


class UserPermission(Enum):
    DELETE_GDM_ARTICLE = "delete:gdm_article"
    DELETE_GDM_MEDICATION = "delete:gdm_medication"
    DELETE_GDM_SMS = "delete:gdm_sms"
    EXPORT_DHOS_DATA = "export:dhos_data"
    EXPORT_WARD_REPORT = "export:ward_report"
    READ_AUDIT_EVENT = "read:audit_event"
    READ_BG_READING = "read:bg_reading"
    READ_BG_READING_ALL = "read:bg_reading_all"
    READ_CLINICIAN = "read:clinician"
    READ_CLINICIAN_ALL = "read:clinician_all"
    READ_DBM_CLINICIAN_ALL = "read:dbm_clinician_all"
    READ_ERROR_MESSAGE = "read:error_message"
    READ_FAILED_REQUEST_QUEUE = "read:failed_request_queue"
    READ_GDM_ACTIVATION = "read:gdm_activation"
    READ_GDM_ANSWER = "read:gdm_answer"
    READ_GDM_ANSWER_ALL = "read:gdm_answer_all"
    READ_GDM_BG_READING = "read:gdm_bg_reading"
    READ_GDM_BG_READING_ALL = "read:gdm_bg_reading_all"
    READ_GDM_CLINICIAN = "read:gdm_clinician"
    READ_GDM_CLINICIAN_ALL = "read:gdm_clinician_all"
    READ_GDM_CSV = "read:gdm_csv"
    READ_GDM_LOCATION = "read:gdm_location"
    READ_GDM_LOCATION_ALL = "read:gdm_location_all"
    READ_GDM_MEDICATION = "read:gdm_medication"
    READ_GDM_MESSAGE = "read:gdm_message"
    READ_GDM_MESSAGE_ALL = "read:gdm_message_all"
    READ_GDM_PATIENT = "read:gdm_patient"
    READ_GDM_PATIENT_ABBREVIATED = "read:gdm_patient_abbreviated"
    READ_GDM_PATIENT_ALL = "read:gdm_patient_all"
    READ_GDM_PDF = "read:gdm_pdf"
    READ_GDM_QUESTION = "read:gdm_question"
    READ_GDM_RULE = "read:gdm_rule"
    READ_GDM_SMS = "read:gdm_sms"
    READ_GDM_SURVEY = "read:gdm_survey"
    READ_GDM_SURVEY_ALL = "read:gdm_survey_all"
    READ_GDM_TELEMETRY = "read:gdm_telemetry"
    READ_GDM_TELEMETRY_ALL = "read:gdm_telemetry_all"
    READ_GDM_TRUSTOMER = "read:gdm_trustomer"
    READ_HL7_MESSAGE = "read:hl7_message"
    READ_LOCATION = "read:location"
    READ_LOCATION_ALL = "read:location_all"
    READ_LOCATION_BY_ODS = "read:location_by_ods"
    READ_MEDICATION = "read:medication"
    READ_PATIENT = "read:patient"
    READ_PATIENT_ALL = "read:patient_all"
    READ_PATIENT_CSV = "read:patient_csv"
    READ_QUESTION = "read:question"
    READ_SEND_CLINICIAN = "read:send_clinician"
    READ_SEND_CLINICIAN_ALL = "read:send_clinician_all"
    READ_SEND_CLINICIAN_TEMP = "read:send_clinician_temp"
    READ_SEND_DEVICE = "read:send_device"
    READ_SEND_ENCOUNTER = "read:send_encounter"
    READ_SEND_ENTRY_IDENTIFIER = "read:send_entry_identifier"
    READ_SEND_LOCATION = "read:send_location"
    READ_SEND_OBSERVATION = "read:send_observation"
    READ_SEND_PATIENT = "read:send_patient"
    READ_SEND_PDF = "read:send_pdf"
    READ_SEND_RULE = "read:send_rule"
    READ_SEND_TRUSTOMER = "read:send_trustomer"
    READ_TRUSTOMER = "read:trustomer"
    READ_WARD_REPORT = "read:ward_report"
    WRITE_ACTIVATION = "write:activation"
    WRITE_ANSWER = "write:answer"
    WRITE_ANSWER_ALL = "write:answer_all"
    WRITE_AUDIT_EVENT = "write:audit_event"
    WRITE_BG_READING = "write:bg_reading"
    WRITE_ERROR_MESSAGE = "write:error_message"
    WRITE_FAILED_REQUEST_QUEUE = "write:failed_request_queue"
    WRITE_GDM_ACTIVATION = "write:gdm_activation"
    WRITE_GDM_ALERT = "write:gdm_alert"
    WRITE_GDM_ANSWER = "write:gdm_answer"
    WRITE_GDM_ANSWER_ALL = "write:gdm_answer_all"
    WRITE_GDM_ARTICLE = "write:gdm_article"
    WRITE_GDM_BG_READING = "write:gdm_bg_reading"
    WRITE_GDM_CLINICIAN = "write:gdm_clinician"
    WRITE_GDM_CLINICIAN_ALL = "write:gdm_clinician_all"
    WRITE_GDM_CSV = "write:gdm_csv"
    WRITE_GDM_LOCATION = "write:gdm_location"
    WRITE_GDM_MEDICATION = "write:gdm_medication"
    WRITE_GDM_MESSAGE = "write:gdm_message"
    WRITE_GDM_MESSAGE_ALL = "write:gdm_message_all"
    WRITE_GDM_PATIENT = "write:gdm_patient"
    WRITE_GDM_PATIENT_ALL = "write:gdm_patient_all"
    WRITE_GDM_PDF = "write:gdm_pdf"
    WRITE_GDM_QUESTION = "write:gdm_question"
    WRITE_GDM_SMS = "write:gdm_sms"
    WRITE_GDM_SURVEY = "write:gdm_survey"
    WRITE_GDM_SURVEY_ALL = "write:gdm_survey_all"
    WRITE_GDM_TELEMETRY = "write:gdm_telemetry"
    WRITE_GDM_TERMS_AGREEMENT = "write:gdm_terms_agreement"
    WRITE_HL7_MESSAGE = "write:hl7_message"
    WRITE_LOCATION = "write:location"
    WRITE_MESSAGE = "write:message"
    WRITE_MESSAGE_ALL = "write:message_all"
    WRITE_PATIENT = "write:patient"
    WRITE_PATIENT_ALL = "write:patient_all"
    WRITE_PATIENT_CSV = "write:patient_csv"
    WRITE_SEND_CLINICIAN = "write:send_clinician"
    WRITE_SEND_CLINICIAN_ALL = "write:send_clinician_all"
    WRITE_SEND_CLINICIAN_TEMP = "write:send_clinician_temp"
    WRITE_SEND_DEVICE = "write:send_device"
    WRITE_SEND_ENCOUNTER = "write:send_encounter"
    WRITE_SEND_LOCATION = "write:send_location"
    WRITE_SEND_OBSERVATION = "write:send_observation"
    WRITE_SEND_PATIENT = "write:send_patient"
    WRITE_SEND_PDF = "write:send_pdf"
    WRITE_SEND_TERMS_AGREEMENT = "write:send_terms_agreement"
    WRITE_TELEMETRY = "write:telemetry"
    WRITE_TERMS_AGREEMENT = "write:terms_agreement"
    WRITE_WARD_REPORT = "write:ward_report"


ROLE_MAPPING: dict[str, list[str]] = {
    UserRole.EPR_SERVICE_ADAPTER.value: [
        UserPermission.READ_HL7_MESSAGE.value,
        UserPermission.WRITE_HL7_MESSAGE.value,
    ],
    UserRole.SYSTEM.value: [
        UserPermission.DELETE_GDM_ARTICLE.value,
        UserPermission.DELETE_GDM_MEDICATION.value,
        UserPermission.DELETE_GDM_SMS.value,
        UserPermission.READ_AUDIT_EVENT.value,
        UserPermission.READ_DBM_CLINICIAN_ALL.value,
        UserPermission.READ_ERROR_MESSAGE.value,
        UserPermission.READ_FAILED_REQUEST_QUEUE.value,
        UserPermission.READ_GDM_ACTIVATION.value,
        UserPermission.READ_GDM_ANSWER_ALL.value,
        UserPermission.READ_GDM_BG_READING_ALL.value,
        UserPermission.READ_GDM_CLINICIAN_ALL.value,
        UserPermission.READ_GDM_LOCATION_ALL.value,
        UserPermission.READ_GDM_MEDICATION.value,
        UserPermission.READ_GDM_MESSAGE_ALL.value,
        UserPermission.READ_GDM_PATIENT_ALL.value,
        UserPermission.READ_GDM_PDF.value,
        UserPermission.READ_GDM_QUESTION.value,
        UserPermission.READ_GDM_RULE.value,
        UserPermission.READ_GDM_SMS.value,
        UserPermission.READ_GDM_SURVEY_ALL.value,
        UserPermission.READ_GDM_TELEMETRY_ALL.value,
        UserPermission.READ_GDM_TELEMETRY.value,
        UserPermission.READ_GDM_TRUSTOMER.value,
        UserPermission.READ_HL7_MESSAGE.value,
        UserPermission.READ_LOCATION_ALL.value,
        UserPermission.READ_LOCATION_BY_ODS.value,
        UserPermission.READ_SEND_CLINICIAN_ALL.value,
        UserPermission.READ_SEND_CLINICIAN.value,
        UserPermission.READ_SEND_DEVICE.value,
        UserPermission.READ_SEND_ENCOUNTER.value,
        UserPermission.READ_SEND_ENTRY_IDENTIFIER.value,
        UserPermission.READ_SEND_LOCATION.value,
        UserPermission.READ_SEND_OBSERVATION.value,
        UserPermission.READ_SEND_PATIENT.value,
        UserPermission.READ_SEND_PDF.value,
        UserPermission.READ_SEND_RULE.value,
        UserPermission.READ_SEND_TRUSTOMER.value,
        UserPermission.READ_WARD_REPORT.value,
        UserPermission.WRITE_AUDIT_EVENT.value,
        UserPermission.WRITE_ERROR_MESSAGE.value,
        UserPermission.WRITE_FAILED_REQUEST_QUEUE.value,
        UserPermission.WRITE_GDM_ACTIVATION.value,
        UserPermission.WRITE_GDM_ALERT.value,
        UserPermission.WRITE_GDM_ARTICLE.value,
        UserPermission.WRITE_GDM_BG_READING.value,
        UserPermission.WRITE_GDM_CLINICIAN_ALL.value,
        UserPermission.WRITE_GDM_CSV.value,
        UserPermission.WRITE_GDM_LOCATION.value,
        UserPermission.WRITE_GDM_MEDICATION.value,
        UserPermission.WRITE_GDM_MESSAGE_ALL.value,
        UserPermission.WRITE_GDM_PATIENT_ALL.value,
        UserPermission.WRITE_GDM_PDF.value,
        UserPermission.WRITE_GDM_QUESTION.value,
        UserPermission.WRITE_GDM_SMS.value,
        UserPermission.WRITE_GDM_SURVEY.value,
        UserPermission.WRITE_GDM_TELEMETRY.value,
        UserPermission.WRITE_GDM_TERMS_AGREEMENT.value,
        UserPermission.WRITE_HL7_MESSAGE.value,
        UserPermission.WRITE_LOCATION.value,
        UserPermission.WRITE_PATIENT_CSV.value,
        UserPermission.WRITE_SEND_CLINICIAN_ALL.value,
        UserPermission.WRITE_SEND_CLINICIAN.value,
        UserPermission.WRITE_SEND_DEVICE.value,
        UserPermission.WRITE_SEND_ENCOUNTER.value,
        UserPermission.WRITE_SEND_LOCATION.value,
        UserPermission.WRITE_SEND_OBSERVATION.value,
        UserPermission.WRITE_SEND_PATIENT.value,
        UserPermission.WRITE_SEND_PDF.value,
        UserPermission.WRITE_WARD_REPORT.value,
    ],
    UserRole.GDM_PATIENT.value: [
        UserPermission.READ_GDM_ANSWER.value,
        UserPermission.READ_GDM_BG_READING.value,
        UserPermission.READ_GDM_MEDICATION.value,
        UserPermission.READ_GDM_MESSAGE.value,
        UserPermission.READ_GDM_PATIENT_ABBREVIATED.value,
        UserPermission.READ_GDM_PATIENT.value,
        UserPermission.READ_GDM_QUESTION.value,
        UserPermission.READ_GDM_RULE.value,
        UserPermission.READ_GDM_SURVEY.value,
        UserPermission.READ_GDM_TELEMETRY.value,
        UserPermission.READ_GDM_TRUSTOMER.value,
        UserPermission.WRITE_GDM_ANSWER.value,
        UserPermission.WRITE_GDM_BG_READING.value,
        UserPermission.WRITE_GDM_MESSAGE.value,
        UserPermission.WRITE_GDM_TELEMETRY.value,
        UserPermission.WRITE_GDM_TERMS_AGREEMENT.value,
    ],
    UserRole.GDM_CLINICIAN.value: [
        UserPermission.READ_GDM_ACTIVATION.value,
        UserPermission.READ_GDM_ANSWER_ALL.value,
        UserPermission.READ_GDM_BG_READING_ALL.value,
        UserPermission.READ_GDM_CLINICIAN.value,
        UserPermission.READ_GDM_CSV.value,
        UserPermission.READ_GDM_LOCATION.value,
        UserPermission.READ_GDM_MEDICATION.value,
        UserPermission.READ_GDM_MESSAGE.value,
        UserPermission.READ_GDM_PATIENT.value,
        UserPermission.READ_GDM_PDF.value,
        UserPermission.READ_GDM_QUESTION.value,
        UserPermission.READ_GDM_TELEMETRY_ALL.value,
        UserPermission.READ_GDM_TRUSTOMER.value,
        UserPermission.WRITE_GDM_ACTIVATION.value,
        UserPermission.WRITE_GDM_ALERT.value,
        UserPermission.WRITE_GDM_ANSWER_ALL.value,
        UserPermission.WRITE_GDM_CLINICIAN.value,
        UserPermission.WRITE_GDM_MESSAGE.value,
        UserPermission.WRITE_GDM_PATIENT.value,
        UserPermission.WRITE_GDM_PDF.value,
        UserPermission.WRITE_GDM_SMS.value,
        UserPermission.WRITE_GDM_SURVEY.value,
        UserPermission.WRITE_GDM_TELEMETRY.value,
        UserPermission.WRITE_GDM_TERMS_AGREEMENT.value,
    ],
    UserRole.GDM_SUPERCLINICIAN.value: [
        UserPermission.READ_GDM_ACTIVATION.value,
        UserPermission.READ_GDM_ANSWER_ALL.value,
        UserPermission.READ_GDM_BG_READING_ALL.value,
        UserPermission.READ_GDM_CLINICIAN_ALL.value,
        UserPermission.READ_GDM_CSV.value,
        UserPermission.READ_GDM_LOCATION_ALL.value,
        UserPermission.READ_GDM_MEDICATION.value,
        UserPermission.READ_GDM_MESSAGE_ALL.value,
        UserPermission.READ_GDM_PATIENT_ALL.value,
        UserPermission.READ_GDM_PDF.value,
        UserPermission.READ_GDM_QUESTION.value,
        UserPermission.READ_GDM_TELEMETRY_ALL.value,
        UserPermission.READ_GDM_TRUSTOMER.value,
        UserPermission.WRITE_GDM_ACTIVATION.value,
        UserPermission.WRITE_GDM_ALERT.value,
        UserPermission.WRITE_GDM_ANSWER_ALL.value,
        UserPermission.WRITE_GDM_CLINICIAN_ALL.value,
        UserPermission.WRITE_GDM_MESSAGE_ALL.value,
        UserPermission.WRITE_GDM_PATIENT_ALL.value,
        UserPermission.WRITE_GDM_PDF.value,
        UserPermission.WRITE_GDM_SMS.value,
        UserPermission.WRITE_GDM_SURVEY.value,
        UserPermission.WRITE_GDM_TELEMETRY.value,
        UserPermission.WRITE_GDM_TERMS_AGREEMENT.value,
    ],
    UserRole.GDM_ADMINISTRATOR.value: [
        UserPermission.DELETE_GDM_ARTICLE.value,
        UserPermission.DELETE_GDM_MEDICATION.value,
        UserPermission.READ_GDM_CLINICIAN_ALL.value,
        UserPermission.READ_GDM_LOCATION_ALL.value,
        UserPermission.READ_GDM_MEDICATION.value,
        UserPermission.READ_GDM_QUESTION.value,
        UserPermission.READ_GDM_TRUSTOMER.value,
        UserPermission.WRITE_GDM_ARTICLE.value,
        UserPermission.WRITE_GDM_CLINICIAN_ALL.value,
        UserPermission.WRITE_GDM_LOCATION.value,
        UserPermission.WRITE_GDM_MEDICATION.value,
        UserPermission.WRITE_GDM_QUESTION.value,
        UserPermission.WRITE_GDM_TELEMETRY.value,
        UserPermission.WRITE_GDM_TERMS_AGREEMENT.value,
    ],
    UserRole.DBM_CLINICIAN.value: [
        UserPermission.READ_BG_READING_ALL.value,
        UserPermission.READ_BG_READING.value,
        UserPermission.READ_CLINICIAN_ALL.value,
        UserPermission.READ_CLINICIAN.value,
        UserPermission.READ_GDM_ACTIVATION.value,
        UserPermission.READ_GDM_ANSWER_ALL.value,
        UserPermission.READ_GDM_BG_READING_ALL.value,
        UserPermission.READ_GDM_CLINICIAN_ALL.value,
        UserPermission.READ_GDM_CSV.value,
        UserPermission.READ_GDM_LOCATION.value,
        UserPermission.READ_GDM_MEDICATION.value,
        UserPermission.READ_GDM_MESSAGE_ALL.value,
        UserPermission.READ_GDM_PATIENT.value,
        UserPermission.READ_GDM_PDF.value,
        UserPermission.READ_GDM_QUESTION.value,
        UserPermission.READ_GDM_TELEMETRY_ALL.value,
        UserPermission.READ_GDM_TRUSTOMER.value,
        UserPermission.READ_LOCATION_ALL.value,
        UserPermission.READ_LOCATION.value,
        UserPermission.READ_MEDICATION.value,
        UserPermission.READ_PATIENT_ALL.value,
        UserPermission.READ_PATIENT_CSV.value,
        UserPermission.READ_PATIENT.value,
        UserPermission.READ_QUESTION.value,
        UserPermission.READ_TRUSTOMER.value,
        UserPermission.WRITE_ACTIVATION.value,
        UserPermission.WRITE_ANSWER_ALL.value,
        UserPermission.WRITE_ANSWER.value,
        UserPermission.WRITE_BG_READING.value,
        UserPermission.WRITE_GDM_ACTIVATION.value,
        UserPermission.WRITE_GDM_ALERT.value,
        UserPermission.WRITE_GDM_ANSWER_ALL.value,
        UserPermission.WRITE_GDM_BG_READING.value,
        UserPermission.WRITE_GDM_CLINICIAN.value,
        UserPermission.WRITE_GDM_MESSAGE_ALL.value,
        UserPermission.WRITE_GDM_PATIENT_ALL.value,
        UserPermission.WRITE_GDM_PATIENT.value,
        UserPermission.WRITE_GDM_PDF.value,
        UserPermission.WRITE_GDM_SMS.value,
        UserPermission.WRITE_GDM_TELEMETRY.value,
        UserPermission.WRITE_GDM_TERMS_AGREEMENT.value,
        UserPermission.WRITE_MESSAGE_ALL.value,
        UserPermission.WRITE_MESSAGE.value,
        UserPermission.WRITE_PATIENT_ALL.value,
        UserPermission.WRITE_PATIENT.value,
        UserPermission.WRITE_TELEMETRY.value,
        UserPermission.WRITE_TERMS_AGREEMENT.value,
    ],
    UserRole.DBM_SUPERCLINICIAN.value: [
        UserPermission.READ_BG_READING_ALL.value,
        UserPermission.READ_BG_READING.value,
        UserPermission.READ_CLINICIAN_ALL.value,
        UserPermission.READ_CLINICIAN.value,
        UserPermission.READ_GDM_ACTIVATION.value,
        UserPermission.READ_GDM_ANSWER_ALL.value,
        UserPermission.READ_GDM_BG_READING_ALL.value,
        UserPermission.READ_GDM_CLINICIAN_ALL.value,
        UserPermission.READ_GDM_CSV.value,
        UserPermission.READ_GDM_LOCATION_ALL.value,
        UserPermission.READ_GDM_MEDICATION.value,
        UserPermission.READ_GDM_MESSAGE_ALL.value,
        UserPermission.READ_GDM_PATIENT_ALL.value,
        UserPermission.READ_GDM_PDF.value,
        UserPermission.READ_GDM_QUESTION.value,
        UserPermission.READ_GDM_TELEMETRY_ALL.value,
        UserPermission.READ_GDM_TRUSTOMER.value,
        UserPermission.READ_LOCATION_ALL.value,
        UserPermission.READ_LOCATION.value,
        UserPermission.READ_MEDICATION.value,
        UserPermission.READ_PATIENT_ALL.value,
        UserPermission.READ_PATIENT_CSV.value,
        UserPermission.READ_PATIENT.value,
        UserPermission.READ_QUESTION.value,
        UserPermission.READ_TRUSTOMER.value,
        UserPermission.WRITE_ACTIVATION.value,
        UserPermission.WRITE_ANSWER_ALL.value,
        UserPermission.WRITE_ANSWER.value,
        UserPermission.WRITE_BG_READING.value,
        UserPermission.WRITE_GDM_ACTIVATION.value,
        UserPermission.WRITE_GDM_ALERT.value,
        UserPermission.WRITE_GDM_ANSWER_ALL.value,
        UserPermission.WRITE_GDM_BG_READING.value,
        UserPermission.WRITE_GDM_CLINICIAN_ALL.value,
        UserPermission.WRITE_GDM_MESSAGE_ALL.value,
        UserPermission.WRITE_GDM_PATIENT_ALL.value,
        UserPermission.WRITE_GDM_PDF.value,
        UserPermission.WRITE_GDM_SMS.value,
        UserPermission.WRITE_GDM_TELEMETRY.value,
        UserPermission.WRITE_GDM_TERMS_AGREEMENT.value,
        UserPermission.WRITE_MESSAGE_ALL.value,
        UserPermission.WRITE_MESSAGE.value,
        UserPermission.WRITE_PATIENT_ALL.value,
        UserPermission.WRITE_PATIENT.value,
        UserPermission.WRITE_TELEMETRY.value,
        UserPermission.WRITE_TERMS_AGREEMENT.value,
    ],
    UserRole.SEND_ENTRY_CLINICIAN.value: [
        UserPermission.READ_SEND_CLINICIAN.value,
        UserPermission.READ_SEND_ENCOUNTER.value,
        UserPermission.READ_SEND_OBSERVATION.value,
        UserPermission.READ_SEND_PATIENT.value,
        UserPermission.READ_SEND_RULE.value,
        UserPermission.READ_SEND_TRUSTOMER.value,
        UserPermission.READ_WARD_REPORT.value,
        UserPermission.WRITE_SEND_ENCOUNTER.value,
        UserPermission.WRITE_SEND_OBSERVATION.value,
        UserPermission.WRITE_SEND_PATIENT.value,
    ],
    UserRole.SEND_CLINICIAN.value: [
        UserPermission.READ_SEND_CLINICIAN.value,
        UserPermission.READ_SEND_ENCOUNTER.value,
        UserPermission.READ_SEND_LOCATION.value,
        UserPermission.READ_SEND_OBSERVATION.value,
        UserPermission.READ_SEND_PATIENT.value,
        UserPermission.READ_SEND_PDF.value,
        UserPermission.READ_SEND_RULE.value,
        UserPermission.READ_SEND_TRUSTOMER.value,
        UserPermission.READ_WARD_REPORT.value,
        UserPermission.WRITE_SEND_ENCOUNTER.value,
        UserPermission.WRITE_SEND_OBSERVATION.value,
        UserPermission.WRITE_SEND_PATIENT.value,
        UserPermission.WRITE_SEND_TERMS_AGREEMENT.value,
    ],
    UserRole.SEND_SUPERCLINICIAN.value: [
        UserPermission.READ_SEND_CLINICIAN_TEMP.value,
        UserPermission.READ_SEND_CLINICIAN.value,
        UserPermission.READ_SEND_ENCOUNTER.value,
        UserPermission.READ_SEND_LOCATION.value,
        UserPermission.READ_SEND_OBSERVATION.value,
        UserPermission.READ_SEND_PATIENT.value,
        UserPermission.READ_SEND_PDF.value,
        UserPermission.READ_SEND_RULE.value,
        UserPermission.READ_SEND_TRUSTOMER.value,
        UserPermission.READ_WARD_REPORT.value,
        UserPermission.WRITE_SEND_CLINICIAN_TEMP.value,
        UserPermission.WRITE_SEND_ENCOUNTER.value,
        UserPermission.WRITE_SEND_OBSERVATION.value,
        UserPermission.WRITE_SEND_PATIENT.value,
        UserPermission.WRITE_SEND_TERMS_AGREEMENT.value,
    ],
    UserRole.SEND_ADMINISTRATOR.value: [
        UserPermission.READ_SEND_CLINICIAN_ALL.value,
        UserPermission.READ_SEND_DEVICE.value,
        UserPermission.READ_SEND_ENCOUNTER.value,
        UserPermission.READ_SEND_LOCATION.value,
        UserPermission.READ_SEND_TRUSTOMER.value,
        UserPermission.WRITE_SEND_CLINICIAN_ALL.value,
        UserPermission.WRITE_SEND_DEVICE.value,
        UserPermission.WRITE_SEND_LOCATION.value,
        UserPermission.WRITE_SEND_TERMS_AGREEMENT.value,
    ],
    UserRole.SEND_ENTRY_DEVICE.value: [
        UserPermission.READ_SEND_DEVICE.value,
        UserPermission.READ_SEND_ENTRY_IDENTIFIER.value,
        UserPermission.READ_SEND_LOCATION.value,
    ],
    UserRole.DEA_COLLECTOR.value: [
        UserPermission.READ_AUDIT_EVENT.value,
        UserPermission.READ_DBM_CLINICIAN_ALL.value,
        UserPermission.READ_GDM_BG_READING_ALL.value,
        UserPermission.READ_GDM_BG_READING.value,
        UserPermission.READ_GDM_CLINICIAN_ALL.value,
        UserPermission.READ_GDM_CLINICIAN.value,
        UserPermission.READ_GDM_LOCATION_ALL.value,
        UserPermission.READ_GDM_LOCATION.value,
        UserPermission.READ_GDM_MEDICATION.value,
        UserPermission.READ_GDM_PATIENT_ALL.value,
        UserPermission.READ_GDM_PATIENT.value,
        UserPermission.READ_GDM_SMS.value,
        UserPermission.READ_SEND_CLINICIAN_ALL.value,
        UserPermission.READ_SEND_CLINICIAN.value,
        UserPermission.READ_SEND_DEVICE.value,
        UserPermission.READ_SEND_ENCOUNTER.value,
        UserPermission.READ_SEND_LOCATION.value,
        UserPermission.READ_SEND_OBSERVATION.value,
        UserPermission.READ_SEND_PATIENT.value,
        UserPermission.READ_SEND_TRUSTOMER.value,
    ],
}


def get_permissions_for_roles(roles: list[str]) -> list[str]:
    return _get_permissions_for_roles_with_lru_cache(frozenset(roles))


@lru_cache
def _get_permissions_for_roles_with_lru_cache(roles: FrozenSet) -> list[str]:
    user_permissions: set[str] = set()
    for r in roles:
        user_permissions |= set(ROLE_MAPPING[r])
    return list(user_permissions)


@lru_cache
def get_role_map() -> dict[str, list[str]]:
    return {r.value: get_permissions_for_roles([r.value]) for r in UserRole}
