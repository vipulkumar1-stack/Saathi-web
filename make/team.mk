# My Team: tests/test_10_add_teammate.py, test_11_add_sourcing_partner.py,
# test_16_add_role.py, test_11b_team_partners.py.

.PHONY: team-partners

##@ Team & roles

# ── Add Teammate tests (4) ─────────────────────────────────────────────────────

add-teammate: ## Add Teammate tests
	pytest tests/test_10_add_teammate.py -v

add-teammate-no-name:
	pytest tests/test_10_add_teammate.py::TestAddTeammate::test_submit_without_full_name -v

add-teammate-no-mobile:
	pytest tests/test_10_add_teammate.py::TestAddTeammate::test_submit_without_mobile -v

add-teammate-no-designation:
	pytest tests/test_10_add_teammate.py::TestAddTeammate::test_submit_without_designation -v

add-teammate-success:
	pytest tests/test_10_add_teammate.py::TestAddTeammate::test_add_teammate_successful -v

# ── Add Sourcing Partner tests (4) ─────────────────────────────────────────────

add-sourcing-partner: ## Add Sourcing Partner tests
	pytest tests/test_11_add_sourcing_partner.py -v

add-sourcing-partner-no-name:
	pytest tests/test_11_add_sourcing_partner.py::TestAddSourcingPartner::test_submit_without_full_name -v

add-sourcing-partner-no-mobile:
	pytest tests/test_11_add_sourcing_partner.py::TestAddSourcingPartner::test_submit_without_mobile -v

add-sourcing-partner-no-email:
	pytest tests/test_11_add_sourcing_partner.py::TestAddSourcingPartner::test_submit_without_email -v

add-sourcing-partner-success:
	pytest tests/test_11_add_sourcing_partner.py::TestAddSourcingPartner::test_add_sourcing_partner_successful -v

# ── Add Role tests (3) ─────────────────────────────────────────────────────────

add-role: ## Add Role tests
	pytest tests/test_16_add_role.py -v

add-role-no-name:
	pytest tests/test_16_add_role.py::TestAddRole::test_add_role_without_name -v

add-role-no-description:
	pytest tests/test_16_add_role.py::TestAddRole::test_add_role_without_description -v

add-role-success:
	pytest tests/test_16_add_role.py::TestAddRole::test_add_role_successfully -v

# ── Team Partners tests (7) ────────────────────────────────────────────────────

team-partners: ## My Team - Partners tests
	pytest tests/test_11b_team_partners.py -v

team-partners-add-picker-roles:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_add_picker_offers_roles -v

team-partners-business-form-fields:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_business_partner_form_fields -v

team-partners-business-submit-enabled:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_business_partner_submit_enabled_when_filled -v

team-partners-business-pan-disables-submit:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_business_partner_pan_disables_submit -v

team-partners-channel-tab-loads:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_channel_partner_tab_loads -v

team-partners-channel-add-sourcing-partner:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_channel_partner_add_is_sourcing_partner -v

team-partners-search-special-chars:
	pytest tests/test_11b_team_partners.py::TestTeamPartners::test_search_handles_special_characters_safely -v
