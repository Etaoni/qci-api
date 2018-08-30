# TODO: this


class DataPackage:
    def __init__(self, access_token, primary_id, secondary_id):
        self._access_token = access_token
        self._primary_id = primary_id
        self._secondary_id = secondary_id

    @property
    def access_token(self):
        return self._access_token

    def to_xml(self):
        datapackage_xml = ''
        datapackage_xml += self._primary_id

        return datapackage_xml

    def validate(self, debug=False):
        if not self.access_token:
            if debug:
                raise ValueError('DataPackage for ID {} failed validation (no access token set)'.format(self.primary_id))
            else:
                return False
        if not self.access_token:
            if debug:
                raise ValueError('DataPackage for ID {} failed validation (no access token set)'.format(self.primary_id))
            else:
                return False

    def __str__(self):
        return self.primary_id
