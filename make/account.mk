# Account & site: tests/test_20b_profile.py, test_24_website_settings.py,
# test_15_raise_query.py, test_25_logout.py.

.PHONY: profile website-settings logout

##@ Account & site

# ── Profile tests (6) ──────────────────────────────────────────────────────────

profile: ## Profile tests
	pytest tests/test_20b_profile.py -v

profile-page-loads:
	pytest tests/test_20b_profile.py::TestProfile::test_profile_page_loads -v

profile-basic-details-fields:
	pytest tests/test_20b_profile.py::TestProfile::test_basic_details_fields -v

profile-tabs-present:
	pytest tests/test_20b_profile.py::TestProfile::test_profile_tabs_present -v

profile-kyc-tab-opens:
	pytest tests/test_20b_profile.py::TestProfile::test_kyc_documents_tab_opens -v

profile-pincode-bug:
	pytest tests/test_20b_profile.py::TestProfile::test_pincode_rejects_non_numeric_bug -v

profile-spoc-xss-safe:
	pytest tests/test_20b_profile.py::TestProfile::test_spoc_name_xss_is_safe -v

# ── Website Settings tests (10) ────────────────────────────────────────────────

website-settings: ## Website Settings tests
	pytest tests/test_24_website_settings.py -v

website-settings-page-loads:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_website_settings_page_loads -v

website-settings-save-buttons:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_all_sections_have_save_buttons -v

website-settings-save-header:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_save_header_section -v

website-settings-save-hero:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_save_hero_section -v

website-settings-save-testimonials:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_save_testimonials_section -v

website-settings-save-calculator:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_save_calculator_section -v

website-settings-save-faq:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_save_faq_section -v

website-settings-edit-hero-heading:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_edit_hero_heading_and_save -v

website-settings-add-feature-row:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_add_feature_adds_row -v

website-settings-add-faq-block:
	pytest tests/test_24_website_settings.py::TestWebsiteSettings::test_add_faq_block -v

# ── Raise a Query tests (3) ────────────────────────────────────────────────────

raise-query: ## Raise a Query tests
	pytest tests/test_15_raise_query.py -v

raise-query-no-issue:
	pytest tests/test_15_raise_query.py::TestRaiseQuery::test_raise_query_without_issue_type -v

raise-query-no-description:
	pytest tests/test_15_raise_query.py::TestRaiseQuery::test_raise_query_without_description -v

raise-query-success:
	pytest tests/test_15_raise_query.py::TestRaiseQuery::test_raise_query_successfully -v

# ── Logout tests (1) ───────────────────────────────────────────────────────────

logout: ## Logout test
	pytest tests/test_25_logout.py -v

logout-redirects:
	pytest tests/test_25_logout.py::TestLogout::test_logout_redirects_to_login -v
