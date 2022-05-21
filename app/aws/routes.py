from . import bp
from flask_restful import Api, Resource, abort, reqparse
import boto3

client_location = boto3.client('location')

api = Api(bp)

class SearchLocationAutoSuggest(Resource):
    """
    This endpoint is for autosuggesting locations for the user. When the
    user finds the location they are searching for, they can then call the
    LocationGeocodeAPI to get the coordinates of that locatio
    """
    def get(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('q', type=str, required=True, help='Type in the name of a location to search', location='args')
        args = self.reqparse.parse_args()
        location_to_search = args['q']
        response = client_location.search_place_index_for_suggestions(
            FilterCountries=['GHA'],
            IndexName='ghana_autocorrect',
            MaxResults=15,
            Text=location_to_search
        )
        return response

class LocationGeocodeAPI(Resource):
    """
    The `location_name` parameter should be passed in the request body of
     the request to search AWS location for that particular location.
     Preferably it should be an exact result previously returned by the
     autocorrect API since when the search is conducted, only the first result is
     going to be used.

     For instance, a user searched 'national' on the autosuggest endpoint and selected a result of 'National Theatre'
     The same exact string 'National Theatre' should be used to query this endpoint and the first
     result will be used to obtain the latitude and longitude of 'National Theatre'
    """
    def get(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('location_name', type=str, required=True, help='Type in the name of the location to search', location='json')
        args = self.reqparse.parse_args()
        location_to_search = args['location_name']
        response = client_location.search_place_index_for_text(
            FilterCountries=['GHA'],
            IndexName='ghana',
            MaxResults=15,
            Text=location_to_search
        )
        return response

api.add_resource(SearchLocationAutoSuggest, '/locations/search/autosuggest', endpoint='autosearch_location_aws')
api.add_resource(LocationGeocodeAPI, '/locations/search/search-text', endpoint='search_by_text')