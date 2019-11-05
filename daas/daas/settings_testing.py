TESTING = True

# Increase the timeout on tests. Otherwise a slow machine will produce some decompilers to throw a timeout error.
# The decompilation timeout for each decompiler on testing mode is "DECOMPILER_TIMEOUT_MULTIPLIER" times the original
# timeout for that decompiler
DECOMPILER_TIMEOUT_MULTIPLIER = 10
