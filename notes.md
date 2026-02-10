Fixed NameError: name 'session' is not defined in analytics_state.py by wrapping the historical performance query in an 'async with rx.asession() as session:' block. This error was originally caused by code removal during merge conflict resolution.

Discovered that navigation directly to '/analytics' resulted in 0% values because the on_load event was missing from the route registration and no institution (selected_hei) was selected by default.

Updated app.py to include 'on_load=AnalyticsState.on_load' in the /analytics route registration.

Modified AnalyticsState.on_load to include a fallback: if no HEI is selected (selected_hei is None), it attempts to fetch the first available institution from the database to ensure data displays even on direct navigation.

Encountered Google AI API rate limit errors (429 RESOURCE_EXHAUSTED) in historical_analytics_state.py when generating insights. Free tier quotas were being exceeded during concurrent or rapid requests.

Implemented exponential backoff retry logic for AI insight generation. The solution includes a loop with a maximum of 5 retries, catching specific rate limit exceptions, and a graceful fallback that allows the application to continue without insights if the quota remains exhausted.