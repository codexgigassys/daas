# Save samples in the DB or not.
SAVE_SAMPLES = True

# If certain sample was not saved due to SAVE_SAMPLE=False, then it will not be able to download
# because it's not saved.
ALLOW_SAMPLE_DOWNLOAD = True

# If the timeout is 0, charts will be always up to date. However, if you have lots of samples and lots of people
# accessing the system, this will produce charts to be regenerated every time.
# Caching the queries is not an option because if a lot of samples enter on the system, the charts will be regenerated
# practically every time someone go to statistics section.
# Also, charts take time to generate, so the statistics section can be loaded significantly faster if the charts
# are on cache.
# Use an integer value in seconds for the timeout.
CHART_TIMEOUT = 1800  # 30 minutes.
