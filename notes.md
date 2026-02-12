Fixed NameError: name 'session' is not defined in analytics_state.py by wrapping the historical performance query in an 'async with rx.asession() as session:' block. This error was originally caused by code removal during merge conflict resolution.

Discovered that navigation directly to '/analytics' resulted in 0% values because the on_load event was missing from the route registration and no institution (selected_hei) was selected by default.

Updated app.py to include 'on_load=AnalyticsState.on_load' in the /analytics route registration.

Modified AnalyticsState.on_load to include a fallback: if no HEI is selected (selected_hei is None), it attempts to fetch the first available institution from the database to ensure data displays even on direct navigation.

Encountered Google AI API rate limit errors (429 RESOURCE_EXHAUSTED) in historical_analytics_state.py when generating insights. Free tier quotas were being exceeded during concurrent or rapid requests.

Implemented exponential backoff retry logic for AI insight generation. The solution includes a loop with a maximum of 5 retries, catching specific rate limit exceptions, and a graceful fallback that allows the application to continue without insights if the quota remains exhausted.

Identified and resolved a frontend display bug on the Historical Data page where year selector cards showed "UNDEFINED% FILLED". Updated HistoricalState in 'app/states/historical_state.py' to ensure year completion percentages default to 0% when no data is present.

Verified database health and confirmed table counts for institutions (12), institution_scores (14), ranking_indicators (14), users (9), and ranking_lenses (5).

Discovered a discrepancy during testing between 'year_completion_data' and the actual attribute 'year_completion_map' in HistoricalState. Confirmed the codebase correctly uses 'year_completion_map'.

Verified that the Reports page status distribution correctly maps to "For Review", "Reviewed", "In Progress", and "Pending" states for both the UI table and analytics pie charts.

Fixed Resend email error handling in auth_state.py. Switched from catching a specific ResendError (which failed due to conditional import mismatches) to catching generic Exception and checking the error string for "testing emails" or "verify a domain".

Optimized logging in AuthState to check for expected Resend test-mode limitations before calling logging.exception, preventing unnecessary backend error logs for known service restrictions.

Fixed text alignment in the "Commit Historical Data" button on the /historical page by adding justify-center and items-center to the inner container elements.

Resolved an issue where Logout did not redirect correctly by changing the event handler to 'yield' the rx.redirect("/") command instead of returning it.

Implemented session-based route protection using a check_auth on_load handler for all sensitive routes. Used replace=True in all auth-related redirects to prevent browser back-button access to protected pages after logout.

Resolved a PostgreSQL ProgrammingError in historical_state.py where ORDER BY expressions in a SELECT DISTINCT query were not in the select list.

Updated HistoricalAnalyticsState to fetch trend data independently via rx.asession() instead of relying on cross-state variables, ensuring data consistency when switching views.

Added auto-selection of the first available institution in HistoricalState.on_load if HEIState.selected_hei is None, mirroring the fix implemented for the main analytics page.