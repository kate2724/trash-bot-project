from SturdyBotHW3Starter import SturdyBot
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
import sys



if __name__ == "__main__":
    config = {"left-motor": OUTPUT_C, "right-motor": OUTPUT_B}
    bot = SturdyBot("bot", configDict=config)
    arg = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    bot.snd.speak("the argument is: " + str(arg))