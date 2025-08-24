Pattern: Test Error Fix Reminder
Test File: test_strategy.py
Test Cases:
test_eod_exit_after_end_of_day

test_hard_stop_loss_exit

test_trend_flip_exit

test_ai_tsl_exit

Error Encountered:
RuntimeError: dictionary changed size during iteration

AttributeError: 'min_profit_mode'

Cause:
The RuntimeError was caused by modifying the open_positions dictionary while iterating over it.

The AttributeError occurred because min_profit_mode was not initialized in the Strategy.__init__ method.

Fix Implemented 👍:
Updated the exit logic loops to iterate over a copy of the dictionary using list(open_positions.items()).

Added self.min_profit_mode = config['MIN_PROFIT_MODE'] to the Strategy.__init__ method.

Outcome:
All strategy exit tests passed 👍

Notes / Reminder:
Always iterate over a copy of a collection if you plan to modify the original during the loop.

Ensure all strategy parameters from constants.py or the config are properly initialized in the Strategy class constructor.