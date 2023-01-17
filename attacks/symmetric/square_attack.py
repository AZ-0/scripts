from spn import SPN

def lambda_set(length=16, max=256, constant=0):
    return [[r] + [constant]*(length - 1) for r in range(max)]

def square_attack(spn: SPN):
    # square attack on 4 rounds
    sets = lambda_set(spn)