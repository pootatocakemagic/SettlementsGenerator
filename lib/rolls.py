from random import randint

def roll_d20(modifier=0):
    return randint(1, 20) + modifier

def roll_dice(face, modifier=0):
    return randint(1, face) + modifier

def transformation_roll(roll, roll_equals):
    for transformed_roll, equal_roll in enumerate(roll_equals):
        if equal_roll[0] <= roll <= equal_roll[1]:
            return transformed_roll + 1
    print('SHIT IN TRANSFORMATION ROLL')
