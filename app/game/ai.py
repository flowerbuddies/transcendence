# several ai approaches:
# 1) ai could move to intercept ball where it will intersect with goal
#       from ball xy, draw an infinite line through ball dxdy, the "path".
#       move paddle to x or y intercept of path and goal
# 2) ai simply tracks ball xy
#       if ball xy > paddle xy, move paddle down/right
#       else move paddle up/left
#
# to humanize ai:
# - occasionally provide ai controller false ball/paddle positions, like totally off locations
# - ball xy could be filtered or randomly offset so that approximate location is known
# - random hesitations before taking action
# - call ai controller less frequently
