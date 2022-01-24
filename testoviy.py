import json


class JsonData:

    def __init__(self, obj_dict: dict):
        self._obj_dict: dict = obj_dict

    def tostr(self) -> str:
        return json.dumps(self._obj_dict)

    def addinfo(self, additional_dict) -> 'JsonData':
        self._obj_dict.update(additional_dict)
        return self


class ParsertoJson:

    def get_json(self, *args, **kwargs) -> JsonData:
        '''
        Create json str
        :param kwargs: find arg in class attributes and add kwarg to json
        :return: json string
        '''
        sup_dict = kwargs
        for k in args:
            if k in self.__dict__ and not kwargs.get(k, False):
                sup_dict[k] = getattr(self, k)
        return JsonData(sup_dict)


class A(ParsertoJson):
    def __init__(self, text):
        self.id = 1
        self.text = text

    def get_json(self, *args, **kwargs) -> JsonData:
        return super().get_json('id', 'text')
