from consent_adk_demo.tools.consent_tools import create_consent, revoke_consent


class TestCreateConsent:
    def test_returns_success_response(self):
        result = create_consent("1234567", "MR", "BB")
        assert result["success"] is True

    def test_contains_correct_operation_name(self):
        result = create_consent("1234567", "MR", "BB")
        assert result["operation"] == "create_consent"

    def test_preserves_input_mac_id(self):
        result = create_consent("7654321", "RR", "PB")
        assert result["mac_id"] == "7654321"

    def test_preserves_input_consent_type(self):
        result = create_consent("1234567", "RP", "BB")
        assert result["consent_type"] == "RP"

    def test_preserves_input_channel(self):
        result = create_consent("1234567", "MR", "PB")
        assert result["channel"] == "PB"

    def test_contains_success_message(self):
        result = create_consent("1234567", "MR", "BB")
        assert "created successfully" in result["message"]


class TestRevokeConsent:
    def test_returns_success_response(self):
        result = revoke_consent("1234567", "MR", "BB")
        assert result["success"] is True

    def test_contains_correct_operation_name(self):
        result = revoke_consent("1234567", "MR", "BB")
        assert result["operation"] == "revoke_consent"

    def test_preserves_input_mac_id(self):
        result = revoke_consent("7654321", "RR", "PB")
        assert result["mac_id"] == "7654321"

    def test_preserves_input_consent_type(self):
        result = revoke_consent("1234567", "RP", "BB")
        assert result["consent_type"] == "RP"

    def test_preserves_input_channel(self):
        result = revoke_consent("1234567", "MR", "PB")
        assert result["channel"] == "PB"

    def test_contains_success_message(self):
        result = revoke_consent("1234567", "MR", "BB")
        assert "revoked successfully" in result["message"]
