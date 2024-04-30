import json

class ListSerializer:
    @staticmethod
    def serialize(lst, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(lst, f, ensure_ascii=False)
    
    @staticmethod
    def deserialize(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            lst = json.load(f)
        return lst