"""UI message strings used in page object locators."""


class CreateLead:
    SUCCESS_TITLE       = "Your Lead Successfully Uploaded"
    DUPLICATE_MOBILE    = "Mobile No. Already Exists"
    ERROR_FIRST_NAME    = "First Name is required"
    ERROR_LAST_NAME     = "Last Name is required"
    ERROR_MOBILE        = "Mobile is required"
    ERROR_LOAN_TYPE     = "Loan Type is required"
    # TODO: confirm exact copy against the live form — guessed from the sibling
    # "<Field> is required" messages above.
    ERROR_EMPLOYMENT    = "Employment Type is required"
    # Confirmed live via the "City is required" toast/paragraph seen in the
    # redesigned modal (2026-09-09) — State was removed as a field entirely,
    # City is now the only location field.
    ERROR_CITY          = "City is required"


class ScheduleFollowup:
    ERROR_DATE    = "Follow-up date is required"
    ERROR_TIME    = "Follow-up time is required"
    ERROR_COMMENT = "Comment is required"


class MoveToLogin:
    SUCCESS             = "Email sent successfully"
    ERROR_LOAN_AMOUNT   = "Login Amount is required"
    ERROR_DATE          = "Please fill in all required fields (Login Amount, Login Date, and Bank)"
    ERROR_LOGIN_ID      = "Please enter Login ID"
    ERROR_BANK          = "Bank is required"
    ERROR_CITY          = "City is required"
    ERROR_BRANCH        = "Branch is required"
    ERROR_BANKER        = "Banker is required"


class MoveToSanction:
    # Verified live on 2026-08-18 (probe_sanction.py): a successful sanction
    # submit shows the SAME toast copy as Move To Login — aliased here rather
    # than duplicated, so the shared string has one source of truth and this
    # class still documents that the equivalence was checked, not assumed.
    SUCCESS             = MoveToLogin.SUCCESS
    ERROR_LOAN_AMOUNT   = "Sanction Amount is required"
    # The root cause of the 2026-08-18 full-suite cascade failure: sanction IDs
    # must match the bank's LAN format (verified live via get_lan_format), the
    # same rule as Login ID. A format violation is only reported at the final
    # "Send Now" step, not at "Request Confirmation".
    ERROR_SANCTION_ID_FORMAT = "Invalid Sanction ID format. Please check and try again."
    # Missing Sanction ID / missing Sanction Date were confirmed live to
    # correctly block the submit (no success toast, lead does not reach
    # Sanctioned), but no distinguishable toast text was captured for either —
    # unlike ERROR_LOAN_AMOUNT and ERROR_SANCTION_ID_FORMAT above, whichever
    # toast they show (if any) either didn't render or auto-dismissed within
    # the single-point-in-time check used to probe it. Needs a live re-check
    # with continuous toast polling across the Send Now click before adding
    # ERROR_SANCTION_ID / ERROR_DATE constants here.


class MoveToDisburse:
    SUCCESS             = "Congratulations for your Disbursement!"
    ERROR_DISBURSED_ID  = "Please enter Disbursement ID"
    ERROR_AMOUNT_DATE   = "Please fill in all required disbursal fields"
    ERROR_EXCEEDS       = "cannot exceed"


class MarkAsLost:
    SUCCESS             = "Lead updated successfully."
    ERROR_REASON        = "Please select reason"
    ERROR_COMMENT       = "Please enter comment"


class CheckOffers:
    # The redesigned Loan Offer Calculator no longer creates a lead; reaching the
    # offers results screen is the success signal. "Share Offers" is a stable
    # control on that screen even when no bank offers are returned for the lead.
    RESULTS_MARKER      = "Share Offers"


class AddTeammate:
    SUCCESS_TITLE           = "Congratulations"
    SUCCESS_TEAMMATE        = "You have Successfully Added Team Member."
    SUCCESS_SOURCING        = "You have successfully added Sub Partner."


class PayoutCalculator:
    RESULT_HEADING      = "Payout Details"


class RaiseQuery:
    SUCCESS             = "Thanks for letting us know!"


class AddRole:
    ROLES_LIST_HEADING  = "Roles And Permission"


class RecommendedDocs:
    SUCCESS = "Success"


class ReassignLeads:
    SUCCESS = "Data updated in the system"


class Cibil:
    PAGE_HEADING       = "Check Cibil Score"
    NO_IMPACT_NOTE     = "Free Checks with No Impact on Score"
    FETCH_SUCCESS      = "PAN details fetched successfully!"
    # Validation copy is confirmed against the live tool (2026).
    ERROR_PAN          = "Please enter a valid 10-digit PAN number."
    ERROR_PAN_CONTINUE = "Please enter a valid PAN number"   # empty-Continue path
    ERROR_FIRST_NAME   = "Please enter first name"
    ERROR_EMAIL        = "Please enter a valid email"
    ERROR_MOBILE       = "Please enter a valid 10-digit mobile number"
    ERROR_DOB          = "Please enter date of birth"
    # Step 2 of the wizard (reached once all details pass validation).
    FULFILMENT_PROMPT  = "Would you like Ambak to fulfil this lead?"


class AbbCalculator:
    PAGE_HEADING  = "ABB Calculator"
    INTRO_PROMPT  = "How would you like to share the income details?"
    PDF_ONLY_NOTE = "Only PDF format allowed"
    OD_CC_NOTE    = "OD/CC accounts not considered"
    RECENT_NOTE   = "Most recent statements required"


class ApfSearch:
    PAGE_HEADING = "APF Finder"
    EMPTY_STATE  = "Builder Not Found"
    COL_BUILDER  = "BUILDER"
    COL_PROJECT  = "PROJECT"
    COL_BANK     = "BANK"


class LeadDetail:
    # Tabs / controls (rendered as buttons on the lead detail page)
    TAB_DETAILS   = "Details"
    TAB_DOCUMENTS = "Documents"
    TAB_HISTORY   = "History"
    # Detail-view cards
    CARD_LOAN     = "Loan Details"
    CARD_CUSTOMER = "Customer Details"
    CARD_INCOME   = "Income Details"
    CARD_PROPERTY = "Property Details"
    # Edit wizard
    EDIT_HEADING  = "Loan Details"
    EDIT_SUCCESS  = "Success"
    # Remarks modal
    REMARK_EMPTY   = "Please enter a remark"
    REMARK_SUCCESS = "Remark saved successfully"
    # Documents
    DOC_SUCCESS    = "Document uploaded successfully"
    # Reopen (lost lead)
    REOPEN_EMPTY   = "Please enter remarks"
    REOPEN_SUCCESS = "Success"


class TeamPartners:
    # "+ Add Teammate" opens a role picker; Business Partner is one role.
    # (Channel Partner has no add form — its add flow is the Sourcing Partner one.)
    ROLE_BUSINESS_PARTNER = "Business Partner"
    ROLE_TEAM_MEMBER      = "Team Member"
    ROLE_SOURCING_PARTNER = "Sourcing Partner"
    TAB_CHANNEL_PARTNER   = "Channel Partner"
    TAB_BUSINESS_PARTNER  = "Business Partner"


class WebsiteSettings:
    # Every section's Save Changes toast follows "<Section> section updated successfully".
    SAVE_SUCCESS   = "updated successfully"
    HERO_SUCCESS   = "Hero section updated successfully"
    HEADER_SUCCESS = "Header section updated successfully"
    FAQ_SUCCESS    = "FAQ section updated successfully"
    SECTIONS = [
        "Header", "Hero Section", "Hero Sub-section", "Services Section",
        "About Us", "Testimonials", "Calculator Section",
        "Lead Creation Journey", "FAQs",
    ]
