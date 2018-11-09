import json
import jsonpickle

# Class defs here
# An a single tag for an image/frame
class Tag(object):
    def __init__(self, x1, x2, y1, y2, width, height, tags):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.width = width # Image width; redundant on each tag
        self.height = height # Image height; redundant on each tag
        self.tags = tags # Classification list for this tag

class VottSession(object):
    def __init__(self, frames, inputTags):
        self.frames = frames # frame to tag list dict
        self.inputTags = inputTags
        self.scd = False

# Given a vott output json, user id param, process as needed and write updates to db
def write_vott_json_to_db():
    # Add jsonpickle fields to json "py/object"
        # "session"/parent json
        # Each Tag
    print('doing nothing')

def main():
    print('hello')

if __name__ == '__main__':
    main()