from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from SturdyBotHW3Starter import SturdyBot


config = {'left-motor':OUTPUT_C, 'right-motor': OUTPUT_B, "medium-motor":OUTPUT_D}
testBot = SturdyBot('testy', config)

# testBot.pointerTurnBy(1500, speed=20)
# testBot.pointerTurnBy(-1500, speed=20)

bttn = testBot.bttn

while not bttn.backspace:
    if bttn.left:
        testBot.pointerTurnBy(100, speed=20)
    elif bttn.right:
        testBot.pointerTurnBy(-100, speed=20)