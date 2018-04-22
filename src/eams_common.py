import logging

# Debugging
def activateLog():
    # to off debugging, change to logging.INFO
#     logging.basicConfig(level=logging.DEBUG)  
#     logging.basicConfig(filename='eams.log', level=logging.DEBUG)   
#     logging.basicConfig(level=logging.INFO)
#     logging.basicConfig(filename='eams.log', level=logging.INFO)
#     logging.basicConfig(level=logging.WARN)  
    pass

def activateLogFile(f):
#     logging.basicConfig(level=logging.DEBUG)
#     logging.basicConfig(filename=f, level=logging.DEBUG)
    logging.basicConfig(filename=f, level=logging.INFO)
#     pass

    