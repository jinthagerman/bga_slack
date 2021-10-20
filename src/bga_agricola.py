"""Utils for agricola"""
import math

def is_harvest_round(progress):
    progress_number = int(progress)
    progress_per_round = 100/14
    harvest_rounds = [4, 7, 9, 11, 13, 14]
    for harvest_round in harvest_rounds:
        abs_progress = progress_per_round * harvest_round
        if math.floor(abs_progress) == progress or math.ceil(abs_progress) == progress:
            return True
    return False
