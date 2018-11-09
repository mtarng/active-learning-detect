import json
import jsonpickle

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

# Single Frame/Image in a VoTT tagging session
class Image(object):
    def __init__(self, image_name, filetype, height, width, tags):
        self.image_name = image_name
        self.tags = tags # List of tags, could be empty

class VottSession(object):
    def __init__(self, frames, inputTags):
        self.frames = frames # frame to tag list dict
        self.inputTags = inputTags
        self.scd = False

def __build_vott_session():
    vott_json = {
        "frames": {
            "1.png": [
                {
                    "x1": 336.95238095238096,
                    "y1": 411.92067988668555,
                    "x2": 419.73809523809524,
                    "y2": 498.94617563739376,
                    "width": 488,
                    "height": 512,
                    "tags": [
                        "baseimageclass1",
                        "baseimageclass2"
                    ]
                }
            ],
            "2.png": [],
            "3.png": [],
            "4.png": [],
            "5.png": [],
            "6.png": [],
            "7.png": []
        },
        "inputTags": "baseimageclass1,baseimageclass2,baseimageclass3,baseimageclass4",
        "scd": False
    }
    return vott_json

def __build_sample_tag():
    tag = {
        "x1": 336.95238095238096,
        "y1": 411.92067988668555,
        "x2": 419.73809523809524,
        "y2": 498.94617563739376,
        "width": 488,
        "height": 512,
        "tags": [
            "classA",
            "classB"
        ]
    }
    return tag

def __build_sample_vott_json():
    tag1 = __build_sample_tag()
    tag2 = __build_sample_tag()
    vott_json = {
        "frames" : {
            "1.png": [],
            "2.png": [tag1, tag2],
            "3.png": []
        },
        "inputTags" : "classA,classB",
        "scd": False
    }
    return vott_json

def main():
    # vott_json = __build_sample_vott_json()
    # print(json.dumps(vott_json))

    vott_session = __build_vott_session()
    print("vott_session")
    print(vott_session)
    print()
    print("json.dumps(vott_session)")
    print(json.dumps(vott_session))
    print()
    
    # Have to json dumps the fake object to decode to object
    picked_session = jsonpickle.decode(json.dumps(vott_session))
    print(type(picked_session))
    print(picked_session)
    # print("picked_session")
    # print(picked_session)
    # print()
    # print("json.dumps(picked_session)")
    # print(json.dumps(picked_session))
    # print()

    # session_object_from_pickle = jsonpickle.encode(picked_session)
    # print("session_object_from_pickle")
    # print(session_object_from_pickle)
    # print()
    # print("json.dumps(session_object_from_pickle)")
    # print(json.dumps(session_object_from_pickle))
    # print()
    # # Seems that dumps is broken on this. Try extracting data from unpicked?
    # print("session_object_from_pickle.frames")
    # print(session_object_from_pickle.frames)
    # print()


    print("trying to create an object first, then pickling...")
    print()

    inputTags = "classA,classB"
    tag1 = Tag(1,10,123.122,149.23,100,200,["classA"])
    tag2 = Tag(40.2,92.190,23.122,49.23,100,200,["classA","classB"])
    
    frames = {"1.png": [tag1, tag2]}

    session = VottSession(frames, inputTags)
    print("session")
    print(session)
    print()

    session_encoded = jsonpickle.encode(session)
    print("session_encoded")
    print(session_encoded)
    print()
    print("json.dumps(session_encoded)")
    print(json.dumps(session_encoded))



    

if __name__ == '__main__':
    main()