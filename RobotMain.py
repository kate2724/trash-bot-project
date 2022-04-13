from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from SturdyBotHW3Starter import SturdyBot
import time

config = {'left-motor':OUTPUT_C, 'right-motor': OUTPUT_B, "medium-motor":OUTPUT_D}
mainBot = SturdyBot('mainBot', config)

def setup():
    startTime = time.time()
    elapsedTime = 0.0
    time_limit= 15

    while elapsedTime < time_limit:
        step()
        elapsedTime = time.time() - startTime
        light = mainBot.readReflect()
        if light >= 10:
            print("Success! elapsed time:", elapsedTime)
            mainBot.stop()
            mainBot.snd.speak("found color")
            break
    if elapsedTime >= time_limit:
        mainBot.stop()
        print("Failure. ran out of time (limit", time_limit, "seconds")
        mainBot.snd.speak("I failed :(")
    mainBot.stop()


def step():
    mainBot.forward(10)